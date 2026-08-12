"""LangGraph assembly: supervisor routes to specialist stubs and back.

Suggested Phase 1 shape:

    START → supervisor → knowledge | diagnostics | ticketing | END
                ↑               |
                └───────────────┘  (specialists always return to supervisor)

Every public invoke MUST pass recursion_limit=25. Hitting that limit is a
routing-prompt bug, not a reason to raise the cap.
"""

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.diagnostics import diagnostics_node
from app.agents.knowledge import knowledge_node
from app.agents.supervisor import RouteClassifier, make_supervisor_node
from app.agents.ticketing import ticketing_node
from app.state import (
    ROUTE_DIAGNOSTICS,
    ROUTE_END,
    ROUTE_KNOWLEDGE,
    ROUTE_TICKETING,
    AgentState,
    NextAgent,
)

RECURSION_LIMIT = 25
DEFAULT_INVOKE_CONFIG = {"recursion_limit": RECURSION_LIMIT}

NODE_SUPERVISOR = "supervisor"
NODE_KNOWLEDGE = ROUTE_KNOWLEDGE
NODE_DIAGNOSTICS = ROUTE_DIAGNOSTICS
NODE_TICKETING = ROUTE_TICKETING


def select_next_agent(state: AgentState) -> NextAgent:
    """Conditional-edge router: read the supervisor's `next_agent` decision."""
    return state.get("next_agent", ROUTE_END)


def build_graph(classifier: RouteClassifier | None = None) -> StateGraph:
    builder = StateGraph(AgentState)
    builder.add_node(NODE_SUPERVISOR, make_supervisor_node(classifier))
    builder.add_node(NODE_KNOWLEDGE, knowledge_node)
    builder.add_node(NODE_DIAGNOSTICS, diagnostics_node)
    builder.add_node(NODE_TICKETING, ticketing_node)

    builder.add_edge(START, NODE_SUPERVISOR)
    builder.add_conditional_edges(
        NODE_SUPERVISOR,
        select_next_agent,
        {
            ROUTE_KNOWLEDGE: NODE_KNOWLEDGE,
            ROUTE_DIAGNOSTICS: NODE_DIAGNOSTICS,
            ROUTE_TICKETING: NODE_TICKETING,
            ROUTE_END: END,
        },
    )
    builder.add_edge(NODE_KNOWLEDGE, NODE_SUPERVISOR)
    builder.add_edge(NODE_DIAGNOSTICS, NODE_SUPERVISOR)
    builder.add_edge(NODE_TICKETING, NODE_SUPERVISOR)
    return builder


def compile_graph(
    classifier: RouteClassifier | None = None,
) -> CompiledStateGraph:
    return build_graph(classifier=classifier).compile()


def invoke_copilot(
    message: str,
    *,
    classifier: RouteClassifier | None = None,
    graph: CompiledStateGraph | None = None,
) -> AgentState:
    """Run one user turn through the graph with the required recursion limit."""
    compiled = graph or compile_graph(classifier=classifier)
    return compiled.invoke(
        {"messages": [HumanMessage(content=message)]},
        DEFAULT_INVOKE_CONFIG,
    )
