# Person A — Phase 2: pgvector extension + document_chunks table

**Goal (from `Implementation_Development_Plan.md`):** the Knowledge Agent
answers real questions from a real (synthetic) knowledge base.

**Person A's specific line item:** "Add the `pgvector` extension and
`document_chunks` table to Postgres."

**Status: complete — verified against a live Postgres.** `docker compose up -d
postgres`, `init_db.py`, and the full `pytest` suite (10 passed, 0 skipped)
all ran clean. The Phase 2 box for this line item is now checked in
`Implementation_Development_Plan.md`.

**Bug caught during verification:** `.env.example` (and the `.env` copied
from it) had `DATABASE_URL=postgresql://...` with no driver suffix. SQLAlchemy
resolves a bare `postgresql://` scheme to the `psycopg2` driver by default,
but this project depends on `psycopg` (v3, via `psycopg[binary]>=3.2` in
`pyproject.toml`) — `psycopg2` was never installed, so `get_engine()` raised
`ModuleNotFoundError: No module named 'psycopg2'` on the first real connection
attempt. Fixed by changing both files to
`postgresql+psycopg://copilot:copilot_dev_password@localhost:5432/copilot`.
This is exactly the class of bug the "not yet verified" status above was
flagging — it could only surface once something actually connected.

Separately: `scripts/init_db.py` fails with `ModuleNotFoundError: No module
named 'app'` if run as `uv run python scripts/init_db.py` from `backend/`
without `PYTHONPATH=.` set first. Running a script directly only puts the
script's own directory on `sys.path`, not `backend/` — pytest doesn't hit this
because it inserts the rootdir itself. Use:
`PYTHONPATH=. uv run python scripts/init_db.py`.

---

## What shipped

- `backend/app/db/models.py` — `DocumentChunk` SQLAlchemy model / `document_chunks` table definition
- `backend/app/db/session.py` — lazy engine/session helpers reading `DATABASE_URL`
- `backend/scripts/init_db.py` — idempotent script: creates the `vector` extension, then the table
- `backend/tests/test_db.py` — 3 tests against a live Postgres; skips cleanly (doesn't fail) if one isn't reachable
- `pgvector>=0.3` added to `backend/pyproject.toml` (the Python package that gives SQLAlchemy the `Vector` column type — distinct from the Postgres `vector` extension, which the init script creates separately)

## Why it's built this way

**No migration tool.** Nothing in this repo uses Alembic (not a dependency, no `migrations/` folder), and Phase 0/1 both favor a lean, script-driven approach over introducing new tooling. `Base.metadata.create_all()` is idempotent and sufficient at this stage — there's no data yet, so "migrations" would just be schema churn with nothing to preserve. If Phase 3's `tickets` table needs a real migration story later, that's the point to reconsider, not now.

**Embedding dimension: 1536 (OpenAI `text-embedding-3-small`).** No embedding model is named anywhere in the project docs — Section 5 of the project overview covers *why pgvector* but not *which embedding model*, and Anthropic doesn't offer an embeddings API, so this was an open decision blocking the table's `vector(n)` column. Confirmed with the user: 1536-dim, the cheap strong-baseline option, matching the doc's own guidance ("don't reach for the fancier/costlier option before you can measure a gap"). This is now `EMBEDDING_DIM` in `models.py`, which `ingest.py` (Phase 2, Person B) should import rather than hardcode.

**`UniqueConstraint("source", "chunk_index")`.** `ingestion/README.md` describes the pipeline as "chunk → embed → **upsert**" — upsert requires something to conflict on. Without this constraint, re-running `ingest.py` after a doc edit (which will happen constantly while the 3 hand-edited demo docs get tuned) would just accumulate duplicate chunks instead of replacing them.

**An HNSW cosine index on `embedding`, added now instead of deferred.** This table's only reason to exist is similarity search — an index for that isn't a future nice-to-have, it's the core operation. `pgvector/pgvector:pg16` (already the Phase 0 base image) supports HNSW natively, so there's no version gap to work around.

**Lazy engine (`get_engine()` behind `@lru_cache`, not a module-level `engine = create_engine(...)`).** Importing `app.db.session` must never fail just because `.env` isn't set up yet — otherwise any test file that happens to import it (even indirectly) would break pytest collection for the *entire* suite, not just DB-dependent tests. This bit immediately during verification (see below) — the first version of `test_db.py` only caught `OperationalError` and crashed on missing `DATABASE_URL` instead of skipping.

**`test_db.py` skips instead of failing when Postgres isn't reachable.** `test_health.py` and `test_routing.py` need no live services — `pytest` alone has always worked from a cold checkout. This is the first genuinely infra-dependent test in the suite; making the whole module skip (not error) when the DB isn't up preserves that "plain `pytest` just works" property for anyone who hasn't run `docker compose up` yet.

## How each part works

**`models.py`.** `DocumentChunk` has `id` (serial PK), `source` (text — the originating file path, e.g. `ingestion/docs/01-vpn-setup.md`), `chunk_index` (int — position within that doc), `content` (text — the raw chunk), `embedding` (`Vector(1536)`), `created_at` (server-side default `now()`). The unique constraint and HNSW index are declared in `__table_args__` so `Base.metadata.create_all()` creates both automatically alongside the table.

**`session.py`.** `get_engine()` loads `.env` from the repo root (same `ROOT`-relative pattern as `scripts/phase0_langsmith_ping.py`), reads `DATABASE_URL`, and builds a `pool_pre_ping=True` engine — cached via `lru_cache` so repeated calls reuse one engine instead of opening a new connection pool each time. `get_session()` hands back a fresh `Session` bound to that engine.

**`scripts/init_db.py`.** Loads `.env`, runs `CREATE EXTENSION IF NOT EXISTS vector`, then `Base.metadata.create_all(engine)`, then queries `pg_extension` and `pg_tables` to print `pgvector_extension_installed=` / `document_chunks_table_exists=` and exits non-zero if either is false — same verification-flag style as `phase0_langsmith_ping.py`.

**`tests/test_db.py`.** A module-level `try`/`except` attempts `SELECT 1`; if that raises `RuntimeError` (no `DATABASE_URL`) or `OperationalError` (Postgres unreachable), the whole module skips with a message telling you what to run first. The three tests that do run check: the `vector` extension is installed, `document_chunks` has the expected columns, and the unique constraint actually rejects a duplicate `(source, chunk_index)` insert (caught as `IntegrityError`).

## What I verified in this session (no Docker/uv available here)

- Built a throwaway venv, installed `sqlalchemy`, `pgvector`, `psycopg[binary]`, `python-dotenv`, `pytest`, and the rest of `backend/pyproject.toml`'s dependencies
- Imported `app.db.models` / `app.db.session` cleanly
- Rendered the actual `CREATE TABLE` and `CREATE INDEX` DDL against the PostgreSQL dialect to catch dialect-specific mistakes before ever touching a real database:
  ```sql
  CREATE TABLE document_chunks (
      id SERIAL NOT NULL,
      source TEXT NOT NULL,
      chunk_index INTEGER NOT NULL,
      content TEXT NOT NULL,
      embedding VECTOR(1536) NOT NULL,
      created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
      PRIMARY KEY (id),
      CONSTRAINT uq_document_chunks_source_chunk_index UNIQUE (source, chunk_index)
  );
  CREATE INDEX ix_document_chunks_embedding_cosine ON document_chunks
      USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
  ```
- Ran the full `backend/tests/` suite: all 6 existing routing/health tests still pass, `test_db.py` skips cleanly with a clear message instead of erroring — caught and fixed a real bug this way (see "Lazy engine" above)
- Deleted the throwaway venv afterward; nothing here touched the repo's real environment

**What I could not verify (this session, no Docker/uv):** that this DDL actually executes against a live `pgvector/pgvector:pg16` instance, and that `test_db.py`'s three real assertions pass.

## Verification (run in a later session, against live Docker — completed)

```powershell
docker compose up -d postgres
# → postgres healthy

cd backend
uv sync --extra dev   # installs pgvector + everything else now in pyproject.toml
PYTHONPATH=. uv run python scripts/init_db.py   # PYTHONPATH needed — see bug note above
# → pgvector_extension_installed=True
# → document_chunks_table_exists=True
# → db_init_ok=true

uv run pytest tests/test_db.py -v
# → 3 passed (not skipped)

uv run pytest -v
# → all tests pass (7 prior + 3 new = 10), 0 skipped
```

Required `DATABASE_URL=postgresql+psycopg://...` in `.env`/`.env.example`
(bare `postgresql://` resolves to the uninstalled `psycopg2` driver — see bug
note above) before `init_db.py` would connect.

Once that's green, check the box in `Implementation_Development_Plan.md` and update the status line above from "code complete" to "complete."
