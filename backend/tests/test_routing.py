"""Routing tests: 3 user messages → 3 correct specialist agents.

Uses a fake Knowledge Agent so graph-routing tests make no provider or database
calls. Retrieval and synthesis behavior is covered independently in
``test_knowledge.py``.
Person A should review these as the Phase 1 [Together] item.
"""

import pytest
from langchain_core.messages import AIMessage

import app.graph as graph_module
from app.graph import (
    DEFAULT_INVOKE_CONFIG,
    RECURSION_LIMIT,
    compile_graph,
    invoke_copilot,
)
from app.state import ROUTE_DIAGNOSTICS, ROUTE_END, ROUTE_KNOWLEDGE, ROUTE_TICKETING


@pytest.fixture(autouse=True)
def fake_knowledge_node(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep routing tests unit-level while the real node reads pgvector."""
    monkeypatch.setattr(
        graph_module,
        "knowledge_node",
        lambda _state: {
            "messages": [AIMessage(content="[knowledge] stub handled: test query")]
        },
    )


def _stub_texts(result: dict) -> list[str]:
    return [
        message.content
        for message in result["messages"]
        if isinstance(message, AIMessage) and isinstance(message.content, str)
    ]


def _assert_only_agent(result: dict, agent: str) -> None:
    texts = _stub_texts(result)
    assert texts, "expected a specialist stub reply"
    assert any(text.startswith(f"[{agent}] stub handled:") for text in texts)
    others = {"knowledge", "diagnostics", "ticketing"} - {agent}
    for other in others:
        assert not any(text.startswith(f"[{other}]") for text in texts)
    assert result["next_agent"] == ROUTE_END


def test_recursion_limit_is_25() -> None:
    assert RECURSION_LIMIT == 25
    assert DEFAULT_INVOKE_CONFIG["recursion_limit"] == 25


def test_vpn_setup_routes_to_knowledge() -> None:
    result = invoke_copilot("How do I set up my VPN?")
    _assert_only_agent(result, ROUTE_KNOWLEDGE)


def test_account_locked_routes_to_diagnostics() -> None:
    result = invoke_copilot("Is my account locked?")
    _assert_only_agent(result, ROUTE_DIAGNOSTICS)


def test_open_ticket_routes_to_ticketing() -> None:
    result = invoke_copilot("Open a ticket for my laptop")
    _assert_only_agent(result, ROUTE_TICKETING)


def test_injected_classifier_is_honored_without_llm() -> None:
    """Prove the graph follows the supervisor even if keywords would disagree."""
    result = invoke_copilot(
        "How do I set up my VPN?",
        classifier=lambda _text: ROUTE_TICKETING,
    )
    _assert_only_agent(result, ROUTE_TICKETING)


def test_compile_graph_is_invocable() -> None:
    graph = compile_graph()
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "How do I set up my VPN?"}]},
        DEFAULT_INVOKE_CONFIG,
    )
    _assert_only_agent(result, ROUTE_KNOWLEDGE)
