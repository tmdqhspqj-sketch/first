"""Tool implementations and Ollama-native tool schemas."""

from datetime import datetime, timezone
from typing import Any


def get_current_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def echo_message(message: str) -> str:
    return message


TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "get_current_time": {
        "description": "Returns the current UTC date and time.",
        "parameters": {"type": "object", "properties": {}, "required": []},
        "fn": lambda _args: get_current_time(),
    },
    "echo": {
        "description": "Echoes the given message back.",
        "parameters": {
            "type": "object",
            "properties": {"message": {"type": "string", "description": "Text to echo"}},
            "required": ["message"],
        },
        "fn": lambda args: echo_message(args.get("message", "")),
    },
}


def ollama_tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": spec["description"],
                "parameters": spec["parameters"],
            },
        }
        for name, spec in TOOL_REGISTRY.items()
    ]


def run_tool(name: str, args: dict | None = None) -> str:
    entry = TOOL_REGISTRY.get(name)
    if not entry:
        return f"Unknown tool: {name}"
    return str(entry["fn"](args or {}))
