from __future__ import annotations

from collections.abc import Iterable
from math import sqrt

from memory_sdk.adapters import FastEmbedEmbeddingProvider, LiteLLMFactExtractor
from memory_sdk.config import MemoryConfig
from memory_sdk.models import MemoryFact
from memory_sdk.pipeline import MemorySavePipeline
from memory_sdk.providers import EmbeddingProvider, FactExtractor
from memory_sdk.storage.sqlite import SQLiteMemoryStore


class Memory:
    """Primary SDK entry point for local save/retrieve operations."""

    def __init__(
        self,
        config: MemoryConfig | None = None,
        *,
        extractor: FactExtractor | None = None,
        embedder: EmbeddingProvider | None = None,
    ) -> None:
        self.config = config or MemoryConfig()
        self.store = SQLiteMemoryStore(self.config.database_path)
        self.extractor = extractor
        self.embedder = embedder
        self._pipeline: MemorySavePipeline | None = None

    def save(
        self,
        *,
        user_id: str,
        key: str,
        value: str,
        kind: str = "fact",
        importance: float = 0.5,
    ) -> MemoryFact:
        """Persist one already-structured memory fact for a user."""
        fact = MemoryFact(
            user_id=user_id,
            key=key,
            value=value,
            kind=kind,
            importance=importance,
        )
        self.store.save_fact(fact)
        return fact

    def save_text(self, *, user_id: str, text: str) -> list[MemoryFact]:
        """Extract, embed, deduplicate, and store durable facts from unstructured text."""
        return self._get_pipeline().save_text(user_id=user_id, text=text)

    def save_many(self, facts: Iterable[MemoryFact]) -> list[MemoryFact]:
        saved = list(facts)
        for fact in saved:
            self.store.save_fact(fact)
        return saved

    def retrieve(self, *, user_id: str, query: str | None = None, limit: int = 10) -> list[MemoryFact]:
        """Retrieve user-scoped facts, preferring sqlite-vec when an embedder is configured."""
        if limit < 1:
            raise ValueError("limit must be at least 1")

        if query and query.strip() and self.embedder is not None:
            query_vectors = self.embedder.embed([query])
            if len(query_vectors) != 1:
                raise ValueError("embedding provider must return exactly one query vector")
            query_vector = query_vectors[0]
            database_ranked = self.store.search_by_vector(
                user_id=user_id,
                query_vector=query_vector,
                limit=limit,
            )
            if database_ranked:
                return database_ranked
        else:
            query_vector = None

        facts = self.store.list_facts(user_id)
        if not query or not query.strip():
            return facts[-limit:][::-1]

        if query_vector is not None:
            vector_ranked = self._rank_vectors(facts, query_vector, limit)
            if vector_ranked:
                return vector_ranked

        return self._rank_lexically(facts, query, limit)

    def _get_pipeline(self) -> MemorySavePipeline:
        if self._pipeline is not None:
            return self._pipeline

        if self.extractor is None:
            if not self.config.llm_model:
                raise ValueError(
                    "save_text requires an extractor or MemoryConfig.llm_model for LiteLLM"
                )
            self.extractor = LiteLLMFactExtractor(self.config.llm_model)
        if self.embedder is None:
            self.embedder = FastEmbedEmbeddingProvider(self.config.embedding_model)

        self._pipeline = MemorySavePipeline(
            store=self.store,
            extractor=self.extractor,
            embedder=self.embedder,
        )
        return self._pipeline

    @staticmethod
    def _rank_vectors(
        facts: list[MemoryFact], query_vector: list[float], limit: int
    ) -> list[MemoryFact]:
        scored: list[tuple[float, float, float, MemoryFact]] = []
        for fact in facts:
            if fact.embedding is None or len(fact.embedding) != len(query_vector):
                continue
            similarity = _cosine_similarity(query_vector, fact.embedding)
            scored.append((similarity, fact.importance, fact.updated_at.timestamp(), fact))
        scored.sort(key=lambda item: item[:3], reverse=True)
        return [item[3] for item in scored[:limit]]

    @staticmethod
    def _rank_lexically(facts: list[MemoryFact], query: str, limit: int) -> list[MemoryFact]:
        terms = {term.casefold() for term in query.split() if term.strip()}

        def score(fact: MemoryFact) -> tuple[int, float, float]:
            haystack = f"{fact.key} {fact.value}".casefold()
            matches = sum(term in haystack for term in terms)
            return matches, fact.importance, fact.updated_at.timestamp()

        ranked = sorted(facts, key=score, reverse=True)
        return [fact for fact in ranked if score(fact)[0] > 0][:limit]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
