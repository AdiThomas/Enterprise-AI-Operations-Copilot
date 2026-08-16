"""Unit tests for retrieval answer formatting; no provider calls are made."""

from app.agents.knowledge import RetrievedChunk, answer_knowledge_query


def test_answer_includes_unique_sources() -> None:
    chunks = [
        RetrievedChunk("ingestion/docs/01-vpn-setup.md", "Use AnyConnect.", 0.1),
        RetrievedChunk("ingestion/docs/01-vpn-setup.md", "Connect to VPN.", 0.2),
        RetrievedChunk("ingestion/docs/02-mfa-account-reset.md", "Use MFA.", 0.3),
    ]

    answer = answer_knowledge_query(
        "How do I set up VPN?",
        retrieve=lambda _query: chunks,
        synthesize=lambda _query, _chunks: "Open Cisco AnyConnect.",
    )

    assert answer.startswith("Open Cisco AnyConnect.")
    assert answer.count("ingestion/docs/01-vpn-setup.md") == 1
    assert "ingestion/docs/02-mfa-account-reset.md" in answer


def test_answer_reports_empty_retrieval() -> None:
    answer = answer_knowledge_query(
        "Unknown process",
        retrieve=lambda _query: [],
        synthesize=lambda _query, _chunks: "should not run",
    )

    assert "could not find relevant documentation" in answer
