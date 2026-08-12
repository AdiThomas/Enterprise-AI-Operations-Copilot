# Contributing

Team working agreements for the Enterprise AI Operations Copilot. Person A
owns backend/data/infra; Person B owns orchestration/RAG/frontend. Do not
swap ownership mid-phase.

## Domain split

| Person A | Person B (this machine) |
|---|---|
| FastAPI backend, Postgres/pgvector, Diagnostics Agent, Ticketing Agent, n8n, Docker/deployment | LangGraph supervisor + routing, human-in-the-loop, Knowledge Agent + RAG pipeline, Next.js frontend, LangSmith + eval |

Pair on every **[Together]** item in `Implementation_Development_Plan.md`.

## Repo and branch strategy

- **Monorepo** — this repository. Do not split frontend/backend into separate remotes.
- **Default branch:** `main`. Never push straight to `main`.
- **Branch names:** `a/<topic>` (Person A) or `b/<topic>` (Person B), e.g. `b/phase-1-supervisor`.
- **PRs:** open against `main`. The other person reviews before merge. No self-merge on shared files (`state.py`, graph wiring, approval resume seam).
- **Force-push:** never to `main`. Feature-branch force-push only if you have not shared that branch.

## Weekly sync

- One pairing session per week on the next **[Together]** item.
- 15-minute async check-in on off days: what landed, what's blocked.
- Treat a phase's definition of done as the milestone, not a calendar date.

Update this section once you pick a standing time.

## API keys and LangSmith (Person B)

Copy `.env.example` to `.env` (gitignored). Fill at least:

1. **Anthropic** — https://console.anthropic.com/settings/keys → `ANTHROPIC_API_KEY`
2. **LangSmith** — https://smith.langchain.com → Settings → API Keys → `LANGSMITH_API_KEY`
3. Keep `LANGSMITH_TRACING=true` and `LANGSMITH_PROJECT=enterprise-ai-copilot`
4. Join the **shared LangSmith org** so both of you see the same traces

Phase 0 Person B check: a trivial traced call appears in the LangSmith UI.
Do not commit `.env` or real keys.

## Local tools (this machine)

Need Python 3.11+, `uv`, Node 20+, `pnpm`, Docker Desktop, Git.

```powershell
uv --version
python --version
node --version
pnpm --version
docker --version
git --version
```
