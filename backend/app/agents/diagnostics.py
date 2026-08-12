"""Diagnostics Agent — Phase 1 stub.

Owned by Person A going forward. This node exists purely so the supervisor
has somewhere real to route "is something broken / locked / down" requests
to, per the Phase 1 "done" bar: a supervisor that routes to hardcoded-reply
stub agents, not real tool calls yet.

Deliberately NOT implemented here (Phase 3 work):
- Calling the mock status API (`/mock/status/{employee_id}`)
- Any read-only tool calls against account/system state
- Structured findings (probable cause, confidence) passed back to the
  supervisor for the Ticketing Agent to act on

Read-only per CLAUDE.md's non-negotiable rules: this agent must never
create tickets, call `create_ticket`, or send notifications — only the
Ticketing and Notification agents may write, and even they must go through
a Phase 4 `interrupt()` approval gate first.
"""

from langchain_core.messages import AIMessage

from app.state import ROUTE_DIAGNOSTICS, AgentState, message_text


def diagnostics_node(state: AgentState) -> dict:
    """Return one canned reply so the graph can route here and terminate.

    Mirrors the shape every Phase 1 specialist stub shares (see
    `knowledge_node`): pull the last message off shared state, echo its
    text back inside a routing-tagged AIMessage. The supervisor sees an
    AIMessage as "this turn is answered" and stops the graph.
    """
    last_message = (state.get("messages") or [None])[-1]
    request_text = message_text(last_message)
    return {
        "messages": [
            AIMessage(content=f"[{ROUTE_DIAGNOSTICS}] stub handled: {request_text}"),
        ],
    }
