"""Knowledge Agent stub.

Person B owns this agent going forward. Phase 2 replaces the canned reply
with retrieval + synthesis over the synthetic corpus.

Read-only: this agent must never create tickets or send notifications.
"""

from langchain_core.messages import AIMessage

from app.state import ROUTE_KNOWLEDGE, AgentState, message_text


def knowledge_node(state: AgentState) -> dict:
    last = (state.get("messages") or [None])[-1]
    text = message_text(last)
    return {
        "messages": [
            AIMessage(content=f"[{ROUTE_KNOWLEDGE}] stub handled: {text}"),
        ],
    }
