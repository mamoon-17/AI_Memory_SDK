from __future__ import annotations

from collections.abc import Iterable

from memory_sdk.config import MemoryConfig
from memory_sdk.models import MemoryFact
from memory_sdk.storage.sqlite import SQLiteMemoryStore


class Memory:
    """Primary SDK entry point for local save/retrieve operations."""

    def __init__(self, config: MemoryConfig | None = None) -> None:
        self.config = config or MemoryConfig()
        self.store = SQLiteMemoryStore(self.config.database_path)

    def save(
        self,
        *,
        user_id: str,
        key: str,
        value: str,
        kind: str = "fact",
        importance: float = 0.5,
    ) -> MemoryFact:
        """Persist one structured memory fact for a user."""
        fact = MemoryFact(
            user_id=user_id,
            key=key,
            value=value,
            kind=kind,
            importance=importance,
        )
        self.store.save_fact(fact)
        return fact

    def save_many(self, facts: Iterable[MemoryFact]) -> list[MemoryFact]:
        saved = list(facts)
        for fact in saved:
            self.store.save_fact(fact)
        return saved

    def retrieve(self, *, user_id: str, query: str | None = None, limit: int = 10) -> list[MemoryFact]:
        """Retrieve user-scoped facts, optionally ranked by simple lexical relevance.

        Phase 0 intentionally keeps retrieval deterministic and dependency-light. A local
        vector ranker will replace the lexical fallback in the next pipeline slice.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")

        facts = self.store.list_facts(user_id)
        if not query or not query.strip():
            return facts[-limit:][::-1]

        terms = {term.casefold() for term in query.split() if term.strip()}

        def score(fact: MemoryFact) -> tuple[int, float, float]:
            haystack = f"{fact.key} {fact.value}".casefold()
            matches = sum(term in haystack for term in terms)
            return matches, fact.importance, fact.updated_at.timestamp()

        ranked = sorted(facts, key=score, reverse=True)
        return [fact for fact in ranked if score(fact)[0] > 0][:limit]
