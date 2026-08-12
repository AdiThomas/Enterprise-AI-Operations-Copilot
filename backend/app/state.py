"""Shared LangGraph state schema for the Operations Copilot.

Phase 1 keeps this small: a message list plus a routing field the
supervisor writes and `add_conditional_edges` reads. Structured
findings (Phase 3) and approval metadata (Phase 4) land here later.
"""

from typing import Annotated, Literal, NotRequired, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph.message import add_messages

AgentName = Literal["knowledge", "diagnostics", "ticketing"]
NextAgent = Literal["knowledge", "diagnostics", "ticketing", "__end__"]

ROUTE_KNOWLEDGE = "knowledge"
ROUTE_DIAGNOSTICS = "diagnostics"
ROUTE_TICKETING = "ticketing"
ROUTE_END = "__end__"


class AgentState(TypedDict):
    """Graph state shared by the supervisor and specialist stubs."""

    messages: Annotated[list[AnyMessage], add_messages]
    next_agent: NotRequired[NextAgent]


def message_text(message: BaseMessage | dict | None) -> str:
    """Best-effort string content from a LangChain message or dict payload."""
    if message is None:
        return ""
    if isinstance(message, dict):
        return str(message.get("content", ""))
    content = getattr(message, "content", message)
    return content if isinstance(content, str) else str(content)
