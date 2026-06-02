from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    query: str
    persona_id: str
    model_id: str
    use_rag: bool
    use_tools: bool
    images: list[str]
    retrieved: list[dict]
    tool_name: str
    tool_result: str
    answer: str
