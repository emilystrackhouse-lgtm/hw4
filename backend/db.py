"""Database access for the Campus Customs API."""

from __future__ import annotations

import os
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = Path(os.getenv("CAMPUS_CUSTOMS_DB", DATA_DIR / "campus_customs.db"))


def query(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Runs a read-only query, so product pages can never change the data."""
    with closing(sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        return con.execute(sql, params).fetchall()


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    """A writable connection that commits on success and rolls back on any error."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        with con:
            yield con
    finally:
        con.close()


def ensure_schema() -> None:
    """Adds the sessions table used for logins (the other tables already exist)."""
    with transaction() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at TEXT NOT NULL
            )
            """
        )
        con.execute("CREATE INDEX IF NOT EXISTS sessions_user_id ON sessions (user_id)")
