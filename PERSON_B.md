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
