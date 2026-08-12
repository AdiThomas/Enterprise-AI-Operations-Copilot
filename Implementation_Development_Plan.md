# Enterprise AI Operations Copilot — Implementation & Development Plan

A working build guide with every task assigned. **[A]** = Person A (backend & data
owner), **[B]** = Person B (orchestration & frontend owner), **[Together]** = do
this one in the same room/call, it's a pairing point or a decision, not a solo task.
Swap in your actual names once you've decided who's who — the labels just need to
stay consistent with who owns what below.

**Rough domain split, for reference:**
| Person A | Person B |
|---|---|
| FastAPI backend, Postgres/pgvector, Diagnostics Agent, Ticketing Agent, n8n, Docker/deployment | LangGraph supervisor + routing, human-in-the-loop, Knowledge Agent + RAG pipeline, Next.js frontend, LangSmith + eval |

If one of you already has a strong preference (e.g. you'd rather own the frontend), swap the whole column — just keep each phase's tasks together rather than splitting a single agent's logic across two people.

---

## Prerequisites (do this before Phase 0) — **[Together]**

- [ X] Python 3.11+, `uv`/`poetry`, Node 20+, `pnpm`, Docker Desktop — both machines
- [ X] Shared GitHub repo, both as collaborators
- [ X] API keys — Anthropic/OpenAI, and a shared LangSmith org with both of you as members
- [X ] Decide: monorepo (recommended), branch strategy, PR review rule, weekly sync time
- [X ] Agree on the domain split above — swap columns now if you want to, not mid-build

**Recommended repo structure:**
```
enterprise-ai-copilot/
├── backend/              # FastAPI + LangGraph app
│   ├── app/
│   │   ├── agents/       # supervisor.py, knowledge.py, diagnostics.py, ticketing.py, notification.py
│   │   ├── tools/        # tool definitions each agent calls
│   │   ├── state.py      # shared graph state schema
│   │   ├── graph.py      # graph assembly
│   │   ├── main.py       # FastAPI app + routes
│   │   └── db/           # SQLAlchemy models, migrations
│   ├── tests/
│   └── pyproject.toml
├── frontend/              # Next.js chat app
├── ingestion/             # RAG corpus + chunking/embedding scripts
│   ├── docs/              # synthetic documentation source files
│   └── ingest.py
├── eval/                  # golden eval sets + RAGAS scripts
├── n8n/                   # exported n8n workflow JSON files
├── docker-compose.yml
└── README.md
```

---

## Phase 0 — Environment & repo setup
**Goal:** Both of you can run `docker compose up` and hit a working health check.

- [X] **[Together]** Create the repo with the structure above
- [X] **[A]** Write `docker-compose.yml` (Postgres+pgvector, Redis, n8n services)
- [X] **[A]** Create `.env.example` listing every required variable
- [X] **[A]** Scaffold FastAPI with a single `/health` route
- [X] **[B]** Confirm `LANGSMITH_TRACING=true` produces a real trace in the LangSmith UI on a trivial test call

**Definition of done:** `docker compose up`, hit `/health`, see `200 OK`, see a test trace in LangSmith. Commit and push. Both A and B Phase 0 tasks are complete.

---

## Phase 1 — Core graph skeleton
**Goal:** The supervisor correctly routes between stub agents.

- [X] **[B]** Define the shared state schema in `state.py` (start simple: a message list)
- [X] **[B]** Write the supervisor node (classifies the request, names the next node)
- [X] **[B]** Write the Knowledge Agent stub (B owns this agent going forward)
- [X] **[A]** Write the Diagnostics and Ticketing Agent stubs (A owns these going forward — good early exposure to the graph code)
- [X] **[B]** Wire `add_conditional_edges` and the return-to-supervisor edges
- [X] **[B]** Set `recursion_limit=25` on `.invoke()` calls
- [X] **[Together]** Write and review the pytest routing tests (3 messages → 3 correct stub agents)

**Definition of done:** All 3 routing tests pass, visible in a LangSmith trace.

---

## Phase 2 — RAG pipeline over real synthetic docs
**Goal:** The Knowledge Agent answers real questions from a real (synthetic) knowledge base.

- [X] **[Together]** Write the one-page fictional company profile (name, industry, size, locations)
- [X] **[Together]** Generate the first-pass batch of IT/network docs with an LLM (5–10 documents)
- [X] **[Together]** Hand-edit the 2–3 documents you'll use in the live demo
- [X] **[A]** Add the `pgvector` extension and `document_chunks` table to Postgres
- [ ] **[B]** Write `ingestion/ingest.py` (chunk → embed → upsert)
- [ ] **[B]** Replace the Knowledge Agent stub with real retrieval + synthesis
- [ ] **[Together]** Write 10–15 golden QA pairs against your own docs
- [ ] **[B]** Run the first RAGAS pass and record baseline scores

**Definition of done:** "How do I set up my VPN?" returns a real, correct answer; baseline RAGAS score committed to the repo.

---

## Phase 3 — Diagnostics + Ticketing agents
**Goal:** Real reads and real writes, with duplicate-write protection from day one.

- [ ] **[A]** Design and create the `tickets` table (with a unique `idempotency_key`)
- [ ] **[A]** Build the mock status API (`/mock/status/{employee_id}`)
- [ ] **[A]** Implement the Diagnostics Agent's read-only tool calls
- [ ] **[A]** Implement the Ticketing Agent's `create_ticket` tool with idempotency key generation
- [ ] **[Together]** Extend the shared state schema to carry structured findings (touches both A's ticket data and B's graph state — a natural pairing point)
- [ ] **[A]** Write the duplicate-ticket idempotency test

**Definition of done:** MFA scenario runs end-to-end through diagnosis and ticket creation (no approval gate yet); duplicate-ticket test passes.

---

## Phase 4 — Human-in-the-loop approval gate
**Goal:** No write action happens without a human clicking approve.

- [ ] **[Together]** List every state-changing action that needs an approval gate
- [ ] **[B]** Wrap those tool calls with `interrupt()`
- [ ] **[A]** Build the `/approvals/pending` and `/approvals/{id}/resume` FastAPI routes
- [ ] **[B]** Wire the resume route to send `Command(resume=...)` back into the graph — **[Together]** pairing session recommended, since this is the seam between A's route and B's graph internals
- [ ] **[B]** Swap in a persistent checkpointer (Postgres/Redis-backed) so pauses survive a restart
- [ ] **[Together]** Test the full MFA scenario end-to-end, including a rejected approval

**Definition of done:** A request visibly pauses, sits pending, and only proceeds after a separate approval call; rejection cleanly stops the flow.

---

## Phase 5 — n8n integration
**Goal:** Approvals and notifications actually reach a human outside your terminal.

- [ ] **[A]** Bring up n8n and build workflow 1: pending-approval webhook → Slack/Teams message
- [ ] **[A]** Build workflow 2: ticket-created webhook → confirmation email/Slack message
- [ ] **[A]** Build the `NotificationAgent` tool that POSTs to the n8n webhook URLs — **[B]** reviews since it's called from inside the graph
- [ ] **[A]** Export both workflows as JSON into `n8n/` in the repo

**Definition of done:** Approving an action produces a real Slack/Teams message within seconds, unattended.

---

## Phase 6 — Frontend
**Goal:** A real chat interface, not curl commands.

- [ ] **[B]** Scaffold the Next.js app
- [ ] **[B]** Build the streaming chat interface (SSE from FastAPI)
- [ ] **[B]** Show which specialist agent handled each step inline
- [ ] **[B]** Build the pending-approvals view, hitting A's Phase 4 routes

**Definition of done:** Full VPN and MFA scenarios run from the browser, start to finish.

---

## Phase 7 — Evaluation hardening
**Goal:** Numbers you can actually put on a resume.

- [ ] **[Together]** Expand the golden eval set to 15–20 pairs per document category
- [ ] **[B]** Set up regression datasets per agent in LangSmith
- [ ] **[Together]** Record routing accuracy, tool-call success rate, RAGAS scores, cost/latency in `eval/results.md`
- [ ] **[B]** Apply model tiering (strong model for supervisor, cheap model for workers) and record the before/after cost delta

**Definition of done:** `eval/results.md` has real, current numbers, including the model-tiering cost comparison.

---

## Phase 8 — Gateway + deployment
**Goal:** A deployed, containerized system with governed model access.

- [ ] **[A]** Build the lightweight custom gateway wrapper (single route, logs model/tokens/cost/caller)
- [ ] **[A]** If Databricks access is available: stand up Unity AI Gateway and swap the wrapper's internals, keeping the same interface
- [ ] **[A]** Write Dockerfiles for `backend` and `frontend`; confirm full-stack `docker compose up` works
- [ ] **[A]** Deploy to Azure (Container Apps/App Service), staying within free-tier limits where possible
- [ ] **[Together]** Confirm the deployed version works end-to-end from a browser

**Definition of done:** A shareable URL running the real system, plus a short `DEPLOYMENT.md`.

---

## Phase 9 (stretch) — Domain expansion

- [ ] **[Together]** Write synthetic security-procedures and HR/handbook content
- [ ] **[B]** Ingest the new categories and re-run the RAGAS eval against the expanded corpus
- [ ] **[Together]** Update resume bullets and interview notes with final numbers

---

## Person A — full task list (backend, data, infra)

- [X] docker-compose.yml, `.env.example`, FastAPI `/health` (Phase 0)
- [X] Diagnostics + Ticketing Agent stubs (Phase 1)
- [X] pgvector extension + `document_chunks` table (Phase 2)
- [ ] `tickets` table, mock status API, Diagnostics Agent tools, `create_ticket` + idempotency (Phase 3)
- [ ] `/approvals` FastAPI routes (Phase 4, paired with B on the resume wiring)
- [ ] n8n workflows 1 & 2, `NotificationAgent` tool, workflow JSON export (Phase 5)
- [ ] Custom gateway wrapper, optional Databricks swap, Dockerfiles, Azure deployment (Phase 8)

## Person B — full task list (orchestration, RAG, frontend)

- [X] LangSmith tracing confirmation (Phase 0)
- [X] State schema, supervisor node, Knowledge Agent stub, conditional edges, recursion limit (Phase 1)
- [ ] `ingest.py`, real Knowledge Agent retrieval, first RAGAS baseline (Phase 2)
- [ ] `interrupt()` wrapping, resume wiring (paired with A), persistent checkpointer (Phase 4)
- [ ] Next.js app, streaming chat UI, agent-attribution display, pending-approvals view (Phase 6)
- [ ] Regression datasets, model tiering + cost comparison (Phase 7)
- [ ] RAG ingestion for stretch-goal document categories, final eval re-run (Phase 9)

---

## Suggested weekly cadence

- One working session together per week minimum, ideally pairing on whichever **[Together]** items are next
- A 15-minute async check-in on off days — what got done, what's blocked
- Review each other's PRs before merging to `main`
- Treat a phase's "definition of done" as the real milestone, not a calendar date — Phase 4 (the approval gate) is worth spending extra time on, since it's doing the most interview-differentiating work

---

## If you get stuck

- **RAG returns irrelevant chunks** → check chunk size first, then confirm the embedding model matches between ingestion and query time
- **Supervisor keeps looping between two agents** → almost always the supervisor prompt missing a clear termination condition, not a graph bug
- **interrupt() doesn't seem to pause** → confirm you're using a persistent checkpointer, not the default in-memory one, if restarting the server between pause and resume
- **n8n webhook never fires** → use the Docker service name, not `localhost`, when calling between containers
