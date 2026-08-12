"""Supervisor node: classify the latest user request and name the next node.

Phase 1 uses a deterministic keyword classifier so routing tests (and local
invokes) do not call a live LLM. Swap `classify_route` for an LLM-backed
classifier in a later phase (SUPERVISOR_MODEL). Do not default to a live
model here — the Anthropic budget is intentionally tiny.
"""

from collections.abc import Callable

from langchain_core.messages import AIMessage

from app.state import (
    ROUTE_DIAGNOSTICS,
    ROUTE_END,
    ROUTE_KNOWLEDGE,
    ROUTE_TICKETING,
    AgentState,
    NextAgent,
    message_text,
)

RouteClassifier = Callable[[str], NextAgent]

# More specific specialists first so "open a ticket about VPN" hits ticketing,
# not knowledge. Default to knowledge for leftover how-to / docs questions.
_TICKETING_HINTS = (
    "ticket",
    "open a",
    "file a",
    "create a ticket",
    "laptop",
)
_DIAGNOSTICS_HINTS = (
    "locked",
    "mfa",
    "2fa",
    "status",
    "account",
    "outage",
    "down",
)
_KNOWLEDGE_HINTS = (
    "how do i",
    "how to",
    "vpn",
    "policy",
    "documentation",
    "setup",
    "set up",
    "reset",
    "password",
)


def classify_route(text: str) -> NextAgent:
    """Keyword classifier used until the supervisor gets a real LLM."""
    lowered = text.lower()
    if any(hint in lowered for hint in _TICKETING_HINTS):
        return ROUTE_TICKETING
    if any(hint in lowered for hint in _DIAGNOSTICS_HINTS):
        return ROUTE_DIAGNOSTICS
    if any(hint in lowered for hint in _KNOWLEDGE_HINTS):
        return ROUTE_KNOWLEDGE
    return ROUTE_KNOWLEDGE


def make_supervisor_node(
    classifier: RouteClassifier | None = None,
) -> Callable[[AgentState], dict]:
    """Build a supervisor node, optionally injecting a test double classifier."""
    classify = classifier or classify_route

    def supervisor_node(state: AgentState) -> dict:
        messages = state.get("messages") or []
        if not messages:
            return {"next_agent": ROUTE_END}

        last = messages[-1]
        # A specialist already replied (AIMessage) → we are done for this turn.
        # Phase 1 stubs handle one specialist hop; multi-agent handoff comes later.
        if isinstance(last, AIMessage):
            return {"next_agent": ROUTE_END}

        route = classify(message_text(last))
        return {"next_agent": route}

    return supervisor_node


supervisor_node = make_supervisor_node()
