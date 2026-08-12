# Person A — Phase 0: Environment & repo setup

**Goal (from `Implementation_Development_Plan.md`):** both people can run
`docker compose up` and hit a working health check.

**Status: complete.** Commits `063f608` and `b56cb48`.

---

## What shipped

- `docker-compose.yml` — Postgres (with the `pgvector` extension baked into
  the image), Redis, n8n
- `.env.example` — every environment variable the stack needs, documented
- `backend/app/main.py` — a FastAPI app with a single `/health` route
- `backend/tests/test_health.py` — proves the route actually works
- Repo scaffold matching the structure in `CLAUDE.md` (`backend/app/agents`,
  `db`, `tools`, plus placeholder dirs for `frontend/`, `ingestion/`,
  `eval/`, `n8n/` that later phases fill in)

## Why it's built this way

**`pgvector/pgvector:pg16` instead of plain `postgres:16`.** The project's
Phase 2 RAG pipeline needs vector similarity search for document retrieval.
Provisioning the pgvector-enabled image from Phase 0 means nobody has to
remember to `CREATE EXTENSION vector;` migrate later, or discover in Phase 2
that the base Postgres image doesn't support it.

**Redis is up before anything uses it.** Redis serves two purposes down the
line: a session cache, and — more importantly — the LangGraph checkpointer
that Phase 4 needs to make `interrupt()` pauses survive a server restart. It
costs nothing to run an unused Redis container now versus debugging a
missing service mid-Phase-4.

**n8n is up before any workflow exists.** Same reasoning — n8n (Phase 5)
needs Basic Auth credentials and a running instance either way, so it's one
less piece of infrastructure to stand up later. `N8N_BASIC_AUTH_ACTIVE` is
set in `docker-compose.yml` so it's never accidentally exposed unauthenticated.

**A single `/health` route, nothing more.** Phase 0's whole job is proving
the scaffolding works end-to-end — API server boots, responds, is testable.
Adding real routes here would be scope creep; the LangGraph app isn't wired
into FastAPI until later (it's invoked directly via `app.graph.invoke_copilot`
in tests for now — see the Phase 1 doc for why).

## How each part works

`backend/app/main.py`:
```python
app = FastAPI(title="Enterprise AI Operations Copilot")

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
```
An async route because the rest of the app (per `CLAUDE.md`) is async
end-to-end — FastAPI's async routes avoid blocking the event loop once real
I/O (DB queries, LLM calls) gets added in later phases. `test_health.py`
hits this with `httpx`'s test client and asserts the exact JSON body.

`.env.example` groups variables by the system that consumes them:
`ANTHROPIC_API_KEY` (LLM calls), `DATABASE_URL` (Postgres, matching the
`docker-compose.yml` credentials), `REDIS_URL`, the `LANGSMITH_*` trio
(tracing — see Person B's Phase 0 doc for the trace-confirmation half of
this), `N8N_WEBHOOK_BASE_URL`, and `SUPERVISOR_MODEL` / `WORKER_MODEL` —
the model-tiering split described in the project overview's Section 5,
set up early so Phase 7's cost comparison has two distinct models to
compare from day one.

## Verification

```powershell
docker compose up -d
# → postgres healthy, redis and n8n running
Invoke-RestMethod http://localhost:8000/health
# → {"status":"ok"}
cd backend; pytest tests/test_health.py -v
# → 1 passed
```
