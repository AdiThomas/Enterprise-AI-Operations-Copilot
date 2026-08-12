# Person B changelog

Running log of Person B work (orchestration, RAG, frontend, LangSmith + eval).
Update this file on every Person B change. Do not put API keys or `.env` contents here.

---

## 2026-08-11 — Phase 0: Environment & LangSmith

**Status:** complete on this machine.

### LangSmith

- Confirmed `LANGSMITH_TRACING=true` with a no-LLM `@traceable` ping (no extra Anthropic spend).
- Project: `enterprise-ai-copilot`
- Run id: `019ff372-1d6f-7410-ae57-d27b307f7a33`
- Name: `phase0_langsmith_ping` (success)
- Trace: https://smith.langchain.com/o/cae38565-c36b-45f6-88b8-1160546c4878/projects/p/0cce058e-8ffc-4570-8222-9ece558ea039/r/019ff372-1d6f-7410-ae57-d27b307f7a33

Repro script (local only; needs `.env`): `backend/scripts/phase0_langsmith_ping.py`

### Local stack

- `docker compose up`: Postgres healthy; Redis and n8n up
- `GET http://localhost:8000/health` → `{"status":"ok"}`

### Tools on this machine

| Tool | Version |
|---|---|
| Git | 2.55.0 |
| Docker | 29.4.3 |
| Python / uv | 3.12 via uv 0.12.3 |
| Node | 24.19.0 |
| pnpm | 11.21.0 |

Also added `CONTRIBUTING.md` (branch/PR agreements) and `eval/README.md` (placeholder for Phase 2/7).

---

## 2026-08-11 — Phase 1: Graph skeleton + routing

**Status:** Person B tasks complete. Diagnostics/Ticketing stubs are placeholders only.

### What changed

- Shared state in `backend/app/state.py`: `messages` + `next_agent`.
- Supervisor node (`backend/app/agents/supervisor.py`) classifies the latest user message and names the next node. Phase 1 uses a deterministic keyword classifier (injectable) so routing does **not** call Anthropic.
- Knowledge Agent stub (`backend/app/agents/knowledge.py`) — B owns this going forward.
- Graph wiring in `backend/app/graph.py`: `add_conditional_edges` from supervisor, specialists return to supervisor, `recursion_limit=25` on every `invoke_copilot()` / `DEFAULT_INVOKE_CONFIG`.
- Pytest routing tests in `backend/tests/test_routing.py` (3 messages → knowledge / diagnostics / ticketing). Person A should review these as the Phase 1 **[Together]** item.

### Person A should take these files

Placeholder stubs so the graph compiles and tests pass. **Do not treat as A's Phase 1 checkbox** — A owns the real Diagnostics/Ticketing work:

- `backend/app/agents/diagnostics.py` — header: "Person A owns this agent going forward."
- `backend/app/agents/ticketing.py` — same. No tools, tickets, or mock status APIs (Phase 3).

### How to run tests

From `backend/` (no live LLM; does not spend Anthropic budget):

```powershell
uv sync --extra dev
uv run pytest
```

Or `pytest` if the venv is already active. Expected: health check + routing tests pass.
