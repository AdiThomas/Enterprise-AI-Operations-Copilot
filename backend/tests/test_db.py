"""Phase 2 (Person A): pgvector extension + document_chunks table.

Requires `.env` set up (copy from `.env.example`) and a live Postgres with
`python scripts/init_db.py` already run (`docker compose up -d postgres`
first). Unlike test_health.py / test_routing.py, this is genuinely
infra-dependent, so the whole module skips cleanly — whether `.env` is
missing, `DATABASE_URL` is unset, or Postgres just isn't reachable — instead
of failing `pytest` for everyone.
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from app.db.models import EMBEDDING_DIM, DocumentChunk
from app.db.session import get_engine, get_session

try:
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
except (RuntimeError, OperationalError) as exc:
    pytest.skip(
        f"Postgres is not reachable ({exc}) — copy .env.example to .env, run "
        "`docker compose up -d postgres`, then `python scripts/init_db.py`",
        allow_module_level=True,
    )


def test_pgvector_extension_installed():
    with get_engine().connect() as conn:
        row = conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        ).fetchone()
    assert row is not None


def test_document_chunks_table_has_expected_columns():
    with get_engine().connect() as conn:
        columns = {
            row[0]
            for row in conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'document_chunks'"
                )
            ).fetchall()
        }
    assert {"id", "source", "chunk_index", "content", "embedding", "created_at"} <= columns


def test_source_chunk_index_unique_constraint_rejects_duplicates():
    session = get_session()
    try:
        session.query(DocumentChunk).filter_by(source="__test__").delete()
        session.commit()

        session.add(
            DocumentChunk(
                source="__test__", chunk_index=0, content="x", embedding=[0.0] * EMBEDDING_DIM
            )
        )
        session.commit()

        session.add(
            DocumentChunk(
                source="__test__", chunk_index=0, content="y", embedding=[0.0] * EMBEDDING_DIM
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    finally:
        session.query(DocumentChunk).filter_by(source="__test__").delete()
        session.commit()
        session.close()
