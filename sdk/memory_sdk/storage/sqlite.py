from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from memory_sdk.models import MemoryFact


class SQLiteMemoryStore:
    """SQLite-backed fact store for the default local profile."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_facts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    importance REAL NOT NULL,
                    embedding_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(memory_facts)").fetchall()
            }
            if "embedding_json" not in columns:
                connection.execute("ALTER TABLE memory_facts ADD COLUMN embedding_json TEXT")
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_facts_user_id ON memory_facts(user_id)"
            )

    def save_fact(self, fact: MemoryFact) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO memory_facts (
                    id, user_id, kind, key, value, importance, embedding_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fact.id,
                    fact.user_id,
                    fact.kind,
                    fact.key,
                    fact.value,
                    fact.importance,
                    json.dumps(fact.embedding) if fact.embedding is not None else None,
                    fact.created_at.isoformat(),
                    fact.updated_at.isoformat(),
                ),
            )

    def list_facts(self, user_id: str) -> list[MemoryFact]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, kind, key, value, importance, embedding_json, created_at, updated_at
                FROM memory_facts
                WHERE user_id = ?
                ORDER BY created_at ASC
                """,
                (user_id,),
            ).fetchall()

        facts: list[MemoryFact] = []
        for row in rows:
            payload = dict(row)
            embedding_json = payload.pop("embedding_json", None)
            payload["embedding"] = json.loads(embedding_json) if embedding_json else None
            facts.append(MemoryFact.model_validate(payload))
        return facts
