# Enterprise AI Operations Copilot

A multi-agent IT support and knowledge assistant, built as a two-person portfolio
project. Full context lives in the two planning docs in this repo root:
`Enterprise_AI_Operations_Copilot_Project_Overview.docx` (architecture, rationale,
security design) and `Implementation_Development_Plan.md` (phase-by-phase build
plan with task ownership). Read both before making architectural decisions.

## Architecture summary

- **Orchestration:** LangGraph supervisor agent routing to specialist agents
  (Knowledge, Diagnostics, Ticketing, Notification)
- **Backend:** FastAPI (async), exposes the LangGraph app over HTTP/streaming
- **Data:** PostgreSQL (tickets, sessions) with the pgvector extension for RAG
  embeddings; Redis for session cache and the LangGraph checkpointer
- **Frontend:** Next.js chat widget
- **Automation:** n8n handles human-facing notifications (Slack/Teams/email) —
  LangGraph handles reasoning, n8n handles "systems meeting"
- **Observability:** LangSmith tracing on every graph run, from day one
- **Data policy:** everything is synthetic — a fictional company, invented
  employees, self-authored documentation. Never ingest real company data.

## Non-negotiable design rules

- Any tool call that changes state (ticket creation, account actions,
  notifications with personal detail) MUST go through a LangGraph `interrupt()`
  human-approval gate before executing. No exceptions for "low risk" cases.
- Every write action needs an idempotency key to prevent duplicate writes on retry.
- Each agent gets only the tools its job requires — Knowledge and Diagnostics
  agents are read-only; only Ticketing and Notification agents can write.
- Set an explicit `recursion_limit` on every graph invocation. If it's ever hit,
  treat that as a bug in the supervisor's routing prompt, not a limit to raise.

## Commands

- `docker compose up` — start Postgres, Redis, and n8n
- `cd backend && uvicorn app.main:app --reload` — run the API locally
- `cd backend && pytest` — run backend tests

## Current phase

Check the checkboxes in `Implementation_Development_Plan.md` to see what's done.
Only work within the current phase unless explicitly asked to jump ahead.
