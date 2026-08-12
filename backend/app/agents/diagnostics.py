"""Diagnostics Agent stub.

Person A owns this agent going forward.

Phase 1: canned reply only so the supervisor can route here. Do not add
real tools, mock status APIs, or account lookups — that is Phase 3.

Read-only: this agent must never create tickets or send notifications.
"""

from langchain_core.messages import AIMessage

from app.state import ROUTE_DIAGNOSTICS, AgentState, message_text


def diagnostics_node(state: AgentState) -> dict:
    last = (state.get("messages") or [None])[-1]
    text = message_text(last)
    return {
        "messages": [
            AIMessage(content=f"[{ROUTE_DIAGNOSTICS}] stub handled: {text}"),
        ],
    }
