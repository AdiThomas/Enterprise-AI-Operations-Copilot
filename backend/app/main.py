"""FastAPI entrypoint for the Enterprise AI Operations Copilot backend.

Phase 0 scope: just a health check. The LangGraph app gets wired in during
Phase 1 (see Implementation_Development_Plan.md).
"""

from fastapi import FastAPI

app = FastAPI(title="Enterprise AI Operations Copilot")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
