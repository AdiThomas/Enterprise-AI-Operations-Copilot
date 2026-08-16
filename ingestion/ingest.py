"""Ingest the synthetic Markdown corpus into Postgres/pgvector.

Run from the repository root:
    uv run --project backend python ingestion/ingest.py

The script is deliberately idempotent: a repeated run replaces chunks with the
same ``(source, chunk_index)`` and removes stale tail chunks from edited files.
It only reads the self-authored synthetic documents in ``ingestion/docs``.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable, Iterable
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DOCS_DIR = ROOT / "ingestion" / "docs"

# Make ``app`` importable when invoked as ``python ingestion/ingest.py``.
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.db.models import DocumentChunk, EMBEDDING_DIM  # noqa: E402
from app.db.session import get_session  # noqa: E402

EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 1_200
CHUNK_OVERLAP = 200

Embedder = Callable[[list[str]], list[list[float]]]


def chunk_markdown(
    text: str, *, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[str]:
    """Split Markdown into bounded, paragraph-aware chunks with overlap."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap smaller than it")

    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        # Preserve headings with the following content where possible. Very long
        # paragraphs are split by words rather than silently truncating content.
        pieces = [paragraph]
        if len(paragraph) > chunk_size:
            words = paragraph.split()
            pieces = []
            piece = ""
            for word in words:
                candidate = f"{piece} {word}".strip()
                if piece and len(candidate) > chunk_size:
                    pieces.append(piece)
                    piece = word
                else:
                    piece = candidate
            if piece:
                pieces.append(piece)

        for piece in pieces:
            candidate = f"{current}\n\n{piece}".strip() if current else piece
            if current and len(candidate) > chunk_size:
                chunks.append(current)
                prefix = current[-overlap:].lstrip()
                current = f"{prefix}\n\n{piece}".strip()
            else:
                current = candidate

    if current:
        chunks.append(current)
    return chunks


def openai_embed(texts: list[str]) -> list[list[float]]:
    """Embed a batch using OpenAI's configured API key."""
    from openai import OpenAI

    client = OpenAI()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    embeddings = [item.embedding for item in response.data]
    if len(embeddings) != len(texts):
        raise RuntimeError("OpenAI returned a different number of embeddings than inputs")
    if any(len(embedding) != EMBEDDING_DIM for embedding in embeddings):
        raise RuntimeError(
            f"Expected {EMBEDDING_DIM}-dimension embeddings from {EMBEDDING_MODEL}"
        )
    return embeddings


def markdown_files(docs_dir: Path = DOCS_DIR) -> Iterable[Path]:
    return sorted(docs_dir.glob("*.md"))


def ingest_file(path: Path, embed: Embedder = openai_embed) -> int:
    """Chunk, embed, and upsert one Markdown file. Return its chunk count."""
    from sqlalchemy import delete
    from sqlalchemy.dialects.postgresql import insert

    source = path.relative_to(ROOT).as_posix()
    chunks = chunk_markdown(path.read_text(encoding="utf-8"))
    if not chunks:
        return 0

    embeddings = embed(chunks)
    rows = [
        {
            "source": source,
            "chunk_index": index,
            "content": content,
            "embedding": embedding,
        }
        for index, (content, embedding) in enumerate(zip(chunks, embeddings, strict=True))
    ]
    statement = insert(DocumentChunk).values(rows)
    statement = statement.on_conflict_do_update(
        constraint="uq_document_chunks_source_chunk_index",
        set_={
            "content": statement.excluded.content,
            "embedding": statement.excluded.embedding,
        },
    )

    session = get_session()
    try:
        session.execute(statement)
        # If an edited document got shorter, remove chunks that no longer exist.
        session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.source == source,
                DocumentChunk.chunk_index >= len(rows),
            )
        )
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    return len(rows)


def ingest_all(docs_dir: Path = DOCS_DIR, embed: Embedder = openai_embed) -> int:
    """Ingest every Markdown document and return the total chunk count."""
    return sum(ingest_file(path, embed=embed) for path in markdown_files(docs_dir))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print chunk counts only")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    files = list(markdown_files())
    if not files:
        raise SystemExit(f"No Markdown files found in {DOCS_DIR}")
    if args.dry_run:
        for path in files:
            print(f"{path.relative_to(ROOT)}: {len(chunk_markdown(path.read_text()))} chunks")
        return
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is not set. Add it to .env before running live ingestion."
        )

    total = ingest_all()
    print(f"Ingested {len(files)} documents and {total} chunks using {EMBEDDING_MODEL}.")


if __name__ == "__main__":
    main()
