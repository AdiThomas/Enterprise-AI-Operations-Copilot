"""SQLAlchemy models for Postgres-backed state.

Phase 2 adds `document_chunks`, the pgvector-backed table `ingestion/ingest.py`
(Phase 2, Person B) will chunk/embed/upsert the synthetic docs corpus into,
and the Knowledge Agent's retrieval will query. Tickets/sessions tables are
Phase 3 (Person A) work and will live in this same file rather than a
separate `Base` per phase.
"""

from __future__ import annotations

import datetime as dt

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# text-embedding-3-small (OpenAI) — 1536 dimensions. No embedding model was
# decided anywhere in the project docs before this table was built; this is
# the cheapest strong-baseline option and the one `ingest.py` (Phase 2,
# Person B) should target. There's no data yet, so changing this later is a
# drop-and-recreate, not a migration.
EMBEDDING_DIM = 1536


class Base(DeclarativeBase):
    pass


class DocumentChunk(Base):
    """One chunk of a synthetic IT/network doc from `ingestion/docs/`.

    `(source, chunk_index)` is unique so `ingest.py` can re-run against an
    edited doc and upsert (ON CONFLICT DO UPDATE) instead of accumulating
    duplicate chunks on every re-ingest.
    """

    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint(
            "source", "chunk_index", name="uq_document_chunks_source_chunk_index"
        ),
        Index(
            "ix_document_chunks_embedding_cosine",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(EMBEDDING_DIM), nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"DocumentChunk(id={self.id!r}, source={self.source!r}, "
            f"chunk_index={self.chunk_index!r})"
        )
