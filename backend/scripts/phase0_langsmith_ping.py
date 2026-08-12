"""Phase 0: confirm LANGSMITH_TRACING=true produces a real LangSmith UI trace.

No LLM call — uses @traceable only, so this does not spend Anthropic credits.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
loaded = load_dotenv(ROOT / ".env")
if not loaded:
    print("ERROR: could not load .env from repo root", file=sys.stderr)
    sys.exit(1)

# Import after env is loaded so tracing env vars are visible.
from langsmith import Client, traceable  # noqa: E402

PROJECT = os.getenv("LANGSMITH_PROJECT", "")
TRACING = os.getenv("LANGSMITH_TRACING", "")
KEY_SET = bool(os.getenv("LANGSMITH_API_KEY"))

print(f"dotenv_loaded={loaded}")
print(f"LANGSMITH_TRACING={TRACING}")
print(f"LANGSMITH_PROJECT={PROJECT}")
print(f"LANGSMITH_API_KEY_set={KEY_SET}")

if TRACING.lower() != "true":
    print("ERROR: LANGSMITH_TRACING is not true", file=sys.stderr)
    sys.exit(1)
if not KEY_SET:
    print("ERROR: LANGSMITH_API_KEY is empty", file=sys.stderr)
    sys.exit(1)
if PROJECT != "enterprise-ai-copilot":
    print(f"ERROR: unexpected LANGSMITH_PROJECT={PROJECT!r}", file=sys.stderr)
    sys.exit(1)


@traceable(name="phase0_langsmith_ping", run_type="chain")
def ping() -> str:
    return "pong"


result = ping()
print(f"function_result={result}")

client = Client()
deadline = time.time() + 30
matched = None
while time.time() < deadline:
    runs = list(
        client.list_runs(
            project_name=PROJECT,
            filter='eq(name, "phase0_langsmith_ping")',
            limit=5,
        )
    )
    if runs:
        matched = runs[0]
        break
    time.sleep(2)

if matched is None:
    print("ERROR: no matching run found in LangSmith after 30s", file=sys.stderr)
    sys.exit(1)

run_url = client.get_run_url(run=matched)
print(f"run_id={matched.id}")
print(f"run_name={matched.name}")
print(f"run_url={run_url}")
print(f"project={PROJECT}")
print("trace_ok=true")
