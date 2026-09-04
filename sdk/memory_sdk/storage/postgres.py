from __future__ import annotations

from typing import Any

from memory_sdk.models import MemoryFact


class PostgresMemoryStore:
    """Optional Postgres + pgvector store for the Standard deployment tier."""

    def __init__(self, dsn: str) -> None:
        if not dsn.strip():
            raise ValueError("Postgres DSN must not be empty")
        self.dsn = dsn
        self._initialize()

    def _connect(self) -> Any:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover - exercised by packaging users
            raise RuntimeError(
                "Postgres storage requires the optional dependency: "
                "pip install 'ai-memory-sdk[postgres]'"
            ) from exc
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_facts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    importance DOUBLE PRECISION NOT NULL,
                    embedding DOUBLE PRECISION[],
                    created_at TIMESTAMPTZ NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL
                )
                """
            )
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
                INSERT INTO memory_facts (
                    id, user_id, kind, key, value, importance, embedding, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    kind = EXCLUDED.kind,
                    key = EXCLUDED.key,
                    value = EXCLUDED.value,
                    importance = EXCLUDED.importance,
                    embedding = EXCLUDED.embedding,
                    created_at = EXCLUDED.created_at,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    fact.id,
                    fact.user_id,
                    fact.kind,
                    fact.key,
                    fact.value,
                    fact.importance,
                    fact.embedding,
                    fact.created_at,
                    fact.updated_at,
                ),
            )

        if fact.embedding:
            self._sync_vector(fact)

    def delete_fact(self, fact_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM memory_facts WHERE id = %s", (fact_id,))
            return cursor.rowcount > 0

    def list_facts(self, user_id: str) -> list[MemoryFact]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, kind, key, value, importance, embedding, created_at, updated_at
                FROM memory_facts
                WHERE user_id = %s
                ORDER BY created_at ASC
                """,
                (user_id,),
            ).fetchall()
        return [_fact_from_row(row) for row in rows]

    def list_user_ids(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT user_id
                FROM memory_facts
                GROUP BY user_id
                ORDER BY lower(user_id) ASC, user_id ASC
                """
            ).fetchall()
        return [str(row["user_id"]) for row in rows]

    def get_fact(self, *, user_id: str, fact_id: str) -> MemoryFact | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, user_id, kind, key, value, importance, embedding, created_at, updated_at
                FROM memory_facts
                WHERE user_id = %s AND id = %s
                """,
                (user_id, fact_id),
            ).fetchone()
        return _fact_from_row(row) if row is not None else None

    def search_by_vector(
        self, *, user_id: str, query_vector: list[float], limit: int
    ) -> list[MemoryFact] | None:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if not query_vector:
            return []

        with self._connect() as connection:
            dimension = self._stored_dimension(connection)
            if dimension is None or dimension != len(query_vector):
                return None
            table_exists = connection.execute(
                "SELECT to_regclass('memory_fact_vectors') AS table_name"
            ).fetchone()
            if table_exists is None or table_exists["table_name"] is None:
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
                    f.embedding,
                    f.created_at,
                    f.updated_at
                FROM memory_fact_vectors AS v
                JOIN memory_facts AS f ON f.id = v.fact_id
                WHERE v.user_id = %s
                ORDER BY v.embedding <=> %s::vector
                LIMIT %s
                """,
                (user_id, _vector_literal(query_vector), limit),
            ).fetchall()
        return [_fact_from_row(row) for row in rows]

    def _sync_vector(self, fact: MemoryFact) -> None:
        if fact.embedding is None:
            return

        with self._connect() as connection:
            if not self._ensure_vector_table(connection, len(fact.embedding)):
                return
            connection.execute(
                """
                INSERT INTO memory_fact_vectors(fact_id, user_id, embedding)
                VALUES (%s, %s, %s::vector)
                ON CONFLICT (fact_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    embedding = EXCLUDED.embedding
                """,
                (fact.id, fact.user_id, _vector_literal(fact.embedding)),
            )

    def _stored_dimension(self, connection: Any) -> int | None:
        row = connection.execute(
            "SELECT value FROM memory_store_metadata WHERE key = 'embedding_dimension'"
        ).fetchone()
        return int(row["value"]) if row is not None else None

    def _ensure_vector_table(self, connection: Any, dimension: int) -> bool:
        if dimension < 1:
            return False

        stored_dimension = self._stored_dimension(connection)
        if stored_dimension is not None and stored_dimension != dimension:
            return False

        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS memory_fact_vectors (
                fact_id TEXT PRIMARY KEY REFERENCES memory_facts(id) ON DELETE CASCADE,
                user_id TEXT NOT NULL,
                embedding vector({dimension}) NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_memory_fact_vectors_user_id
            ON memory_fact_vectors(user_id)
            """
        )
        if stored_dimension is None:
            connection.execute(
                """
                INSERT INTO memory_store_metadata(key, value)
                VALUES ('embedding_dimension', %s)
                ON CONFLICT (key) DO NOTHING
                """,
                (str(dimension),),
            )
            self._backfill_vectors(connection, dimension)
        return True

    @staticmethod
    def _backfill_vectors(connection: Any, dimension: int) -> None:
        rows = connection.execute(
            """
            SELECT id, user_id, embedding
            FROM memory_facts
            WHERE embedding IS NOT NULL
            """
        ).fetchall()
        for row in rows:
            embedding = row["embedding"]
            if not isinstance(embedding, list) or len(embedding) != dimension:
                continue
            connection.execute(
                """
                INSERT INTO memory_fact_vectors(fact_id, user_id, embedding)
                VALUES (%s, %s, %s::vector)
                ON CONFLICT (fact_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    embedding = EXCLUDED.embedding
                """,
                (row["id"], row["user_id"], _vector_literal(embedding)),
            )


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(format(float(value), ".17g") for value in vector) + "]"


def _fact_from_row(row: Any) -> MemoryFact:
    payload = dict(row)
    embedding = payload.get("embedding")
    payload["embedding"] = list(embedding) if embedding is not None else None
    return MemoryFact.model_validate(payload)
