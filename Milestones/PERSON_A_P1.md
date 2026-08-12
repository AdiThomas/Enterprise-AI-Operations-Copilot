# Person A — Phase 1: Core graph skeleton (Diagnostics + Ticketing stubs)

**Goal (from `Implementation_Development_Plan.md`):** the supervisor
correctly routes between stub agents. Per the project overview docx, the
Phase 1 "done" bar project-wide is: *"Supervisor routes to 2–3 stub agents
with hardcoded responses; LangSmith tracing is on from the start."*

**Person A's specific line item:** "Write the Diagnostics and Ticketing
Agent stubs (A owns these going forward — good early exposure to the graph
code)."

**Status: complete**, written directly by Person A (earlier, functionally
identical placeholder files existed but were authored by Person B purely to
unblock the graph/tests — see git history on `backend/app/agents/*.py`;
this pass replaces them with A's own).

---

## What shipped

- `backend/app/agents/diagnostics.py` — the Diagnostics Agent stub
- `backend/app/agents/ticketing.py` — the Ticketing Agent stub
- Both already wired into `backend/app/graph.py` (no changes needed there)
  and already covered by `backend/tests/test_routing.py`

## Why it's built this way

**Both stubs are one function, no branching, no tools.** Phase 1's entire
purpose is proving the *graph shape* works — supervisor classifies a
request, hands off to a specialist node, that node replies, control returns
to the supervisor, the supervisor sees the reply and stops. Real logic
(mock status API calls for Diagnostics, `create_ticket` + idempotency for
Ticketing) is explicitly Phase 3 work. Building that now would mean
debugging two things at once — the graph wiring and the business logic —
instead of proving the wiring first on a trivial payload.

**Diagnostics is read-only, Ticketing is (future) write-capable.** This
maps directly to `CLAUDE.md`'s non-negotiable rules: *"Each agent gets only
the tools its job requires — Knowledge and Diagnostics agents are
read-only; only Ticketing and Notification agents can write."* Right now
neither stub has any tools at all, so this distinction is purely
documented intent (in the docstrings) rather than enforced code — but it's
worth stating up front because Phase 3 will hand Ticketing a real
`create_ticket` tool, and Phase 4 will require that tool to sit behind an
`interrupt()` approval gate before it can execute. Getting the ownership
boundary right now avoids having to retrofit it later.

**Both stubs mirror `knowledge_node` exactly.** Person B's Knowledge Agent
stub (`backend/app/agents/knowledge.py`) established the pattern all three
specialists use:

```python
def knowledge_node(state: AgentState) -> dict:
    last = (state.get("messages") or [None])[-1]
    text = message_text(last)
    return {"messages": [AIMessage(content=f"[knowledge] stub handled: {text}")]}
```

Diagnostics and Ticketing follow the identical shape so that `graph.py`
can treat all three nodes uniformly (`add_node` + a return edge back to the
supervisor), and so the routing tests can assert on all three with the
same helper function. Deviating from this shape for no reason would just
make the graph harder to reason about.

## How each part works

**The state contract (`backend/app/state.py`).** `AgentState` is a
`TypedDict` with two fields: `messages` (a running list, merged via
LangGraph's `add_messages` reducer) and `next_agent` (what the supervisor
decided). `ROUTE_DIAGNOSTICS = "diagnostics"` and `ROUTE_TICKETING =
"ticketing"` are the exact string keys both the supervisor's routing
decision and `graph.py`'s `add_conditional_edges` mapping use — get these
strings wrong anywhere and the graph silently mis-routes instead of
erroring, so both stubs import the constants rather than hardcoding the
strings.

**Inside `diagnostics_node` / `ticketing_node`:**
1. `(state.get("messages") or [None])[-1]` — grab the most recent message
   defensively (empty state shouldn't crash the node).
2. `message_text(last_message)` — a helper in `state.py` that pulls a
   plain string out of either a LangChain message object or a raw dict
   (the routing tests exercise both call shapes — see
   `test_compile_graph_is_invocable`, which invokes with a plain dict
   payload).
3. Return `{"messages": [AIMessage(content=f"[{ROUTE_X}] stub handled: {text}")]}`
   — LangGraph merges this single-item list into shared state via the
   `add_messages` reducer; it doesn't replace the whole history.

**How the supervisor actually reaches these nodes.** `supervisor_node`
(`backend/app/agents/supervisor.py`) runs a deterministic keyword
classifier (`classify_route`) against the latest human message — no LLM
call in Phase 1, which keeps routing tests free and fast. It writes the
result into `state["next_agent"]`. `graph.py`'s `select_next_agent`
function reads that field, and `add_conditional_edges` uses it to pick
which node runs next: `knowledge` / `diagnostics` / `ticketing` / `END`.
After a specialist stub runs, its edge points straight back to
`NODE_SUPERVISOR`; the supervisor sees the last message is now an
`AIMessage` (not a fresh human message) and returns `ROUTE_END`, so the
graph terminates after exactly one specialist hop.

**Why the return message is prefixed `[diagnostics] stub handled: ...`.**
This isn't just cosmetic — it's the contract the tests assert on.
`test_routing.py::_assert_only_agent` checks that the reply starts with
`f"[{agent}] stub handled:"` *and* that no other agent's prefix shows up in
the same result, which is what actually proves routing worked correctly
(not just that some agent replied).

## What Phase 3 adds on top (without changing this contract)

- Diagnostics gains real read-only tool calls against
  `/mock/status/{employee_id}`
- Ticketing gains a `create_ticket` tool with a generated
  `idempotency_key`, writing rows to a real `tickets` Postgres table
- The shared state schema grows a structured-findings field so Diagnostics
  can hand a probable cause + confidence to Ticketing instead of the
  supervisor re-parsing free text out of the chat transcript
- None of this requires touching how `graph.py` wires these nodes in, or
  the routing contract itself — only what happens *inside* each node

## Verification

```powershell
cd backend
uv sync --extra dev   # or: pip install -e ".[dev]"
pytest tests/test_routing.py -v
```
Expected: 6 passed —
`test_recursion_limit_is_25`,
`test_vpn_setup_routes_to_knowledge`,
`test_account_locked_routes_to_diagnostics`,
`test_open_ticket_routes_to_ticketing`,
`test_injected_classifier_is_honored_without_llm`,
`test_compile_graph_is_invocable`.
