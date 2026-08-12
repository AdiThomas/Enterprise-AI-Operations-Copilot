"""Ticketing Agent — Phase 1 stub.

Owned by Person A going forward. This node exists purely so the supervisor
has somewhere real to route "open a ticket" requests to, per the Phase 1
"done" bar: a supervisor that routes to hardcoded-reply stub agents, not
real writes yet.

Deliberately NOT implemented here (Phase 3 work):
- The `tickets` table (with a unique `idempotency_key` column)
- The `create_ticket` tool and idempotency-key generation
- Any actual row written to Postgres

This is the first agent in the system that will eventually hold write
access. Per CLAUDE.md's non-negotiable rules, once `create_ticket` is real
(Phase 3) it must sit behind a Phase 4 `interrupt()` human-approval gate —
no ticket gets created, and no account gets touched, without a human
clicking approve first. That gate does not exist yet, so this stub cannot
write anything regardless.
"""

from langchain_core.messages import AIMessage

from app.state import ROUTE_TICKETING, AgentState, message_text


def ticketing_node(state: AgentState) -> dict:
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
            AIMessage(content=f"[{ROUTE_TICKETING}] stub handled: {request_text}"),
        ],
    }
