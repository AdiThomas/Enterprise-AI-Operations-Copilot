# Enterprise AI Operations Copilot

Multi-agent IT support and knowledge assistant. See `CLAUDE.md` for the project
context Claude Code reads automatically, and the two planning docs (project
overview + implementation plan) for full detail.

## Quickstart

1. Copy `.env.example` to `.env` and fill in your API keys
2. `docker compose up` — starts Postgres (with pgvector), Redis, and n8n
3. `cd backend && pip install -e ".[dev]"` (or `uv sync`)
4. `uvicorn app.main:app --reload` — runs the API on http://localhost:8000
5. Check `GET /health` returns `{"status": "ok"}`

n8n is available at http://localhost:5678 (user: `admin`, password from
`docker-compose.yml` — change it before this goes anywhere near production).

## Status

Phase 0 scaffold. See `Implementation_Development_Plan.md` for what's next.
