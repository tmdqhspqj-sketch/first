import json
import re
from typing import Any, Literal

from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.agent.tools import TOOL_REGISTRY, ollama_tool_schemas, run_tool
from app.services.config_loader import get_model, get_persona
from app.services.ollama import ollama_client
from app.services.rag import rag_store

TOOL_CALL_PATTERN = re.compile(r"\[TOOL:(\w+)(?:\|(\{.*?\}))?\]", re.DOTALL)


def _resolve_model_name(model_cfg: dict) -> str:
    return model_cfg.get("ollama_model") or "gemma4:e4b"


def _build_system_prompt(persona_id: str, context: str, use_tools: bool) -> str:
    persona = get_persona(persona_id) or get_persona("assistant") or {}
    base = persona.get("system_prompt", "You are a helpful assistant.")
    forbidden = persona.get("forbidden") or []
    rules = "\n".join(f"- {f}" for f in forbidden) if forbidden else ""
    tool_hint = ""
    if use_tools and TOOL_REGISTRY:
        names = ", ".join(TOOL_REGISTRY.keys())
        tool_hint = f"\nYou have function tools: {names}. Call them when needed."
    ctx_block = f"\n\n### Retrieved context\n{context}" if context else "\n\n### Retrieved context\n(none)"
    return f"{base}\n\n### Rules\n{rules}{tool_hint}{ctx_block}"


def _build_user_message(query: str, images: list[str] | None) -> dict[str, Any]:
    msg: dict[str, Any] = {"role": "user", "content": query}
    if images:
        msg["images"] = images
    return msg


async def retrieve_node(state: AgentState) -> dict:
    if not state.get("use_rag", True):
        return {"retrieved": []}
    hits = await rag_store.search(state["query"], k=4)
    return {"retrieved": hits}


async def generate_node(state: AgentState) -> dict:
    model_cfg = get_model(state.get("model_id", "default")) or get_model("default") or {}
    model_name = _resolve_model_name(model_cfg)
    temperature = float(model_cfg.get("temperature", 0.7))
    top_p = float(model_cfg.get("top_p", 0.9))
    num_ctx = int(model_cfg.get("num_ctx", 8192))
    use_tools = bool(state.get("use_tools"))

    context_parts = [h["content"] for h in state.get("retrieved", [])]
    context = "\n---\n".join(context_parts)
    system = _build_system_prompt(state.get("persona_id", "assistant"), context, use_tools)

    messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for m in state.get("messages", []):
        role = m.get("role", "user") if isinstance(m, dict) else getattr(m, "type", "user")
        content = m.get("content", "") if isinstance(m, dict) else getattr(m, "content", "")
        if role in ("human", "user"):
            role = "user"
        elif role in ("ai", "assistant"):
            role = "assistant"
        entry: dict[str, Any] = {"role": role, "content": content}
        if isinstance(m, dict) and m.get("images"):
            entry["images"] = m["images"]
        messages.append(entry)

    has_user = any(m["role"] == "user" for m in messages[1:])
    if not has_user:
        messages.append(_build_user_message(state["query"], state.get("images")))

    tools = ollama_tool_schemas() if use_tools else None
    raw = await ollama_client.chat(
        messages,
        model_name,
        temperature=temperature,
        top_p=top_p,
        num_ctx=num_ctx,
        tools=tools,
        stream=False,
    )
    assert isinstance(raw, str)

    if raw.strip().startswith("{") and "tool_calls" in raw:
        return {"answer": raw}
    return {"answer": raw}


def _parse_native_tool_calls(answer: str) -> list[dict] | None:
    try:
        data = json.loads(answer)
    except json.JSONDecodeError:
        return None
    calls = data.get("tool_calls")
    return calls if isinstance(calls, list) and calls else None


def should_use_tool(state: AgentState) -> Literal["tool", "end"]:
    if not state.get("use_tools"):
        return "end"
    answer = state.get("answer", "")
    if _parse_native_tool_calls(answer):
        return "tool"
    if TOOL_CALL_PATTERN.search(answer):
        return "tool"
    return "end"


async def tool_node(state: AgentState) -> dict:
    answer = state.get("answer", "")
    native = _parse_native_tool_calls(answer)
    if native:
        results: list[str] = []
        names: list[str] = []
        for call in native:
            fn = call.get("function", {})
            name = fn.get("name", "")
            args_raw = fn.get("arguments", "{}")
            try:
                args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
            except json.JSONDecodeError:
                args = {}
            if not isinstance(args, dict):
                args = {}
            result = run_tool(name, args)
            names.append(name)
            results.append(f"[Tool {name}]: {result}")
        combined = "\n".join(results)
        return {
            "tool_name": ", ".join(names),
            "tool_result": combined,
            "answer": combined,
        }

    match = TOOL_CALL_PATTERN.search(answer)
    if not match:
        return {"tool_result": ""}
    name = match.group(1)
    args_raw = match.group(2)
    args: dict = {}
    if args_raw:
        try:
            args = json.loads(args_raw)
        except json.JSONDecodeError:
            args = {}
    result = run_tool(name, args)
    clean = TOOL_CALL_PATTERN.sub("", answer).strip()
    combined = f"{clean}\n\n[Tool {name}]: {result}".strip()
    return {"tool_name": name, "tool_result": result, "answer": combined}


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("tool", tool_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_conditional_edges("generate", should_use_tool, {"tool": "tool", "end": END})
    graph.add_edge("tool", END)
    return graph.compile()


agent_graph = build_agent_graph()


async def run_agent(
    query: str,
    *,
    messages: list | None = None,
    persona_id: str = "assistant",
    model_id: str = "default",
    use_rag: bool = True,
    use_tools: bool = False,
    images: list[str] | None = None,
) -> dict:
    initial: AgentState = {
        "messages": messages or [],
        "query": query,
        "persona_id": persona_id,
        "model_id": model_id,
        "use_rag": use_rag,
        "use_tools": use_tools,
        "images": images or [],
        "retrieved": [],
        "tool_name": "",
        "tool_result": "",
        "answer": "",
    }
    result = await agent_graph.ainvoke(initial)
    return {
        "answer": result.get("answer", ""),
        "retrieved": result.get("retrieved", []),
        "tool_name": result.get("tool_name", ""),
        "tool_result": result.get("tool_result", ""),
    }
