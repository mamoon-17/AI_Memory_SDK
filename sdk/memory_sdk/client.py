from __future__ import annotations

from collections.abc import Iterable
from math import sqrt

from memory_sdk.adapters import FastEmbedEmbeddingProvider, LiteLLMFactExtractor
from memory_sdk.config import MemoryConfig
from memory_sdk.models import MemoryFact
from memory_sdk.pipeline import MemorySavePipeline
from memory_sdk.providers import EmbeddingProvider, FactExtractor
from memory_sdk.quality import recency_score
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
        """Extract, score, embed, deduplicate, and store durable facts from unstructured text."""
        return self._get_pipeline().save_text(user_id=user_id, text=text)

    def save_many(self, facts: Iterable[MemoryFact]) -> list[MemoryFact]:
        saved = list(facts)
        for fact in saved:
            self.store.save_fact(fact)
        return saved

    def forget(self, *, user_id: str, memory_id: str) -> bool:
        """Delete one memory only when it belongs to the requested user scope."""
        fact = self.store.get_fact(user_id=user_id, fact_id=memory_id)
        if fact is None:
            return False
        return self.store.delete_fact(memory_id)

    def retrieve(self, *, user_id: str, query: str | None = None, limit: int = 10) -> list[MemoryFact]:
        """Retrieve user-scoped facts with relevance, importance, and recency ranking."""
        if limit < 1:
            raise ValueError("limit must be at least 1")

        if query and query.strip() and self.embedder is not None:
            query_vectors = self.embedder.embed([query])
            if len(query_vectors) != 1:
                raise ValueError("embedding provider must return exactly one query vector")
            query_vector = query_vectors[0]
            candidate_limit = min(max(limit * 4, limit), 100)
            database_ranked = self.store.search_by_vector(
                user_id=user_id,
                query_vector=query_vector,
                limit=candidate_limit,
            )
            if database_ranked:
                return self._rank_vectors(database_ranked, query_vector, limit)
        else:
            query_vector = None

        facts = self.store.list_facts(user_id)
        if not query or not query.strip():
            ranked = sorted(facts, key=self._quality_score, reverse=True)
            return ranked[:limit]

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

    @classmethod
    def _rank_vectors(
        cls, facts: list[MemoryFact], query_vector: list[float], limit: int
    ) -> list[MemoryFact]:
        scored: list[tuple[float, float, MemoryFact]] = []
        for fact in facts:
            if fact.embedding is None or len(fact.embedding) != len(query_vector):
                continue
            similarity = _cosine_similarity(query_vector, fact.embedding)
            combined = (0.70 * similarity) + (0.20 * fact.importance) + (0.10 * recency_score(fact.updated_at))
            scored.append((combined, fact.updated_at.timestamp(), fact))
        scored.sort(key=lambda item: item[:2], reverse=True)
        return [item[2] for item in scored[:limit]]

    @classmethod
    def _rank_lexically(cls, facts: list[MemoryFact], query: str, limit: int) -> list[MemoryFact]:
        terms = {term.casefold() for term in query.split() if term.strip()}
        if not terms:
            return []

        scored: list[tuple[float, float, MemoryFact]] = []
        for fact in facts:
            haystack = f"{fact.key} {fact.value}".casefold()
            matches = sum(term in haystack for term in terms)
            if matches == 0:
                continue
            lexical_relevance = matches / len(terms)
            combined = (
                (0.70 * lexical_relevance)
                + (0.20 * fact.importance)
                + (0.10 * recency_score(fact.updated_at))
            )
            scored.append((combined, fact.updated_at.timestamp(), fact))
        scored.sort(key=lambda item: item[:2], reverse=True)
        return [item[2] for item in scored[:limit]]

    @staticmethod
    def _quality_score(fact: MemoryFact) -> tuple[float, float]:
        combined = (0.70 * fact.importance) + (0.30 * recency_score(fact.updated_at))
        return combined, fact.updated_at.timestamp()


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
