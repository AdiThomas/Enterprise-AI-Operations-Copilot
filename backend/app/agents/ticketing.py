"""Ticketing Agent stub.

Person A owns this agent going forward.

Phase 1: canned reply only so the supervisor can route here. Do not add
create_ticket, idempotency keys, or a tickets table — that is Phase 3.

Write-capable in later phases (after the Phase 4 interrupt() approval gate).
"""

from langchain_core.messages import AIMessage

from app.state import ROUTE_TICKETING, AgentState, message_text


def ticketing_node(state: AgentState) -> dict:
    last = (state.get("messages") or [None])[-1]
    text = message_text(last)
    return {
        "messages": [
            AIMessage(content=f"[{ROUTE_TICKETING}] stub handled: {text}"),
        ],
    }
