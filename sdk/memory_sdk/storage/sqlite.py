from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

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

    def _vector_connection(self) -> tuple[sqlite3.Connection, Any] | None:
        connection = self._connect()
        sqlite_vec = _load_sqlite_vec(connection)
        if sqlite_vec is None:
            connection.close()
            return None
        return connection, sqlite_vec

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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
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

        if fact.embedding:
            self._sync_vector(fact)

    def delete_fact(self, fact_id: str) -> bool:
        """Delete one fact and its vector entry when sqlite-vec is available."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT rowid FROM memory_facts WHERE id = ?", (fact_id,)
            ).fetchone()
        if row is None:
            return False
        rowid = row["rowid"]

        vector_connection = self._vector_connection()
        if vector_connection is not None:
            connection, _sqlite_vec = vector_connection
            try:
                table = connection.execute(
                    """
                    SELECT 1 FROM sqlite_master
                    WHERE type = 'table' AND name = 'memory_fact_vectors'
                    """
                ).fetchone()
                if table is not None:
                    connection.execute("DELETE FROM memory_fact_vectors WHERE rowid = ?", (rowid,))
                    connection.commit()
            except sqlite3.Error:
                pass
            finally:
                connection.close()

        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM memory_facts WHERE id = ?", (fact_id,))
            return cursor.rowcount > 0

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

        return [_fact_from_row(row) for row in rows]

    def search_by_vector(
        self, *, user_id: str, query_vector: list[float], limit: int
    ) -> list[MemoryFact] | None:
        """Run sqlite-vec KNN search, or return None when the extension cannot be used."""
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if not query_vector:
            return []

        vector_connection = self._vector_connection()
        if vector_connection is None:
            return None

        connection, sqlite_vec = vector_connection
        try:
            if not self._ensure_vector_table(connection, len(query_vector), sqlite_vec):
                return None
            rows = connection.execute(
                """
                SELECT
                    f.id,
                    f.user_id,
                    f.kind,
                    f.key,
                    f.value,
                    f.importance,
                    f.embedding_json,
                    f.created_at,
                    f.updated_at
                FROM memory_fact_vectors AS v
                JOIN memory_facts AS f ON f.rowid = v.rowid
                WHERE v.embedding MATCH ?
                  AND v.user_id = ?
                  AND k = ?
                ORDER BY distance
                """,
                (sqlite_vec.serialize_float32(query_vector), user_id, limit),
            ).fetchall()
            return [_fact_from_row(row) for row in rows]
        except sqlite3.Error:
            return None
        finally:
            connection.close()

    def _sync_vector(self, fact: MemoryFact) -> None:
        if fact.embedding is None:
            return

        vector_connection = self._vector_connection()
        if vector_connection is None:
            return

        connection, sqlite_vec = vector_connection
        try:
            if not self._ensure_vector_table(connection, len(fact.embedding), sqlite_vec):
                return
            row = connection.execute(
                "SELECT rowid FROM memory_facts WHERE id = ?", (fact.id,)
            ).fetchone()
            if row is None:
                return
            rowid = row["rowid"]
            connection.execute("DELETE FROM memory_fact_vectors WHERE rowid = ?", (rowid,))
            connection.execute(
                """
                INSERT INTO memory_fact_vectors(rowid, embedding, user_id)
                VALUES (?, ?, ?)
                """,
                (rowid, sqlite_vec.serialize_float32(fact.embedding), fact.user_id),
            )
            connection.commit()
        except sqlite3.Error:
            return
        finally:
            connection.close()

    def _ensure_vector_table(
        self, connection: sqlite3.Connection, dimension: int, sqlite_vec: Any
    ) -> bool:
        if dimension < 1:
            return False

        row = connection.execute(
            "SELECT value FROM memory_store_metadata WHERE key = 'embedding_dimension'"
        ).fetchone()
        if row is not None and int(row["value"]) != dimension:
            return False

        connection.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fact_vectors USING vec0(
                embedding float[{dimension}],
                user_id text
            )
            """
        )
        if row is None:
            connection.execute(
                """
                INSERT INTO memory_store_metadata(key, value)
                VALUES ('embedding_dimension', ?)
                """,
                (str(dimension),),
            )
            self._backfill_vectors(connection, dimension, sqlite_vec)
        connection.commit()
        return True

    @staticmethod
    def _backfill_vectors(connection: sqlite3.Connection, dimension: int, sqlite_vec: Any) -> None:
        rows = connection.execute(
            """
            SELECT rowid, user_id, embedding_json
            FROM memory_facts
            WHERE embedding_json IS NOT NULL
            """
        ).fetchall()
        for row in rows:
            embedding = json.loads(row["embedding_json"])
            if not isinstance(embedding, list) or len(embedding) != dimension:
                continue
            connection.execute(
                """
                INSERT INTO memory_fact_vectors(rowid, embedding, user_id)
                VALUES (?, ?, ?)
                """,
                (row["rowid"], sqlite_vec.serialize_float32(embedding), row["user_id"]),
            )


def _load_sqlite_vec(connection: sqlite3.Connection) -> Any | None:
    try:
        import sqlite_vec
    except ImportError:
        return None

    try:
        connection.enable_load_extension(True)
        sqlite_vec.load(connection)
    except (AttributeError, OSError, sqlite3.Error):
        return None
    finally:
        try:
            connection.enable_load_extension(False)
        except (AttributeError, sqlite3.Error):
            pass
    return sqlite_vec


def _fact_from_row(row: sqlite3.Row) -> MemoryFact:
    payload = dict(row)
    embedding_json = payload.pop("embedding_json", None)
    payload["embedding"] = json.loads(embedding_json) if embedding_json else None
    return MemoryFact.model_validate(payload)
