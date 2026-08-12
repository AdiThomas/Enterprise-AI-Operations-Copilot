"""FastAPI entrypoint for the Enterprise AI Operations Copilot backend.

Phase 1: /health only. The LangGraph supervisor lives in app.graph
(invoke via invoke_copilot); HTTP/streaming exposure comes later.
"""

from fastapi import FastAPI

app = FastAPI(title="Enterprise AI Operations Copilot")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
