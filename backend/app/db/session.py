"""SQLAlchemy engine/session for Postgres.

Lazy on purpose: importing this module never touches the network or reads
`DATABASE_URL` — only `get_engine()` / `get_session()` do. That keeps pytest
collection (and any test that doesn't need the database) working even when
`.env` isn't set up or Postgres isn't running.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    load_dotenv(ROOT / ".env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set — copy .env.example to .env and fill it in"
        )
    return create_engine(url, pool_pre_ping=True)


def get_session() -> Session:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False)()
