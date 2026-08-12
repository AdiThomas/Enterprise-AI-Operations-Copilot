"""Phase 2 (Person A): create the pgvector extension and document_chunks table.

Run once against a running Postgres (docker compose up -d postgres). Safe to
re-run — CREATE EXTENSION IF NOT EXISTS and metadata.create_all are both
idempotent, so this never drops or duplicates anything.
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[2]
if not load_dotenv(ROOT / ".env"):
    print("ERROR: could not load .env from repo root", file=sys.stderr)
    sys.exit(1)

from app.db.models import Base  # noqa: E402
from app.db.session import get_engine  # noqa: E402

engine = get_engine()

with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

Base.metadata.create_all(engine)

with engine.connect() as conn:
    ext = conn.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
    ).fetchall()
    tables = conn.execute(
        text("SELECT tablename FROM pg_tables WHERE tablename = 'document_chunks'")
    ).fetchall()

print(f"pgvector_extension_installed={bool(ext)}")
print(f"document_chunks_table_exists={bool(tables)}")

if not (ext and tables):
    print("ERROR: setup did not complete as expected", file=sys.stderr)
    sys.exit(1)

print("db_init_ok=true")
