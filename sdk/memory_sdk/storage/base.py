from __future__ import annotations

from typing import Protocol

from memory_sdk.models import MemoryFact


class MemoryStore(Protocol):
    """Storage contract shared by the default SQLite and optional Standard-tier stores."""

    def save_fact(self, fact: MemoryFact) -> None: ...

    def delete_fact(self, fact_id: str) -> bool: ...

    def list_facts(self, user_id: str) -> list[MemoryFact]: ...

    def list_user_ids(self) -> list[str]: ...

    def get_fact(self, *, user_id: str, fact_id: str) -> MemoryFact | None: ...

    def search_by_vector(
        self, *, user_id: str, query_vector: list[float], limit: int
    ) -> list[MemoryFact] | None: ...
