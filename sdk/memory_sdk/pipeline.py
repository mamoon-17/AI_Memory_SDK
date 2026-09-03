from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from memory_sdk.models import MemoryFact
from memory_sdk.providers import EmbeddingProvider, ExtractedFact, FactExtractor
from memory_sdk.storage.sqlite import SQLiteMemoryStore


class PipelineState(TypedDict, total=False):
    user_id: str
    text: str
    should_store: bool
    extracted: list[ExtractedFact]
    deduped: list[ExtractedFact]
    embeddings: list[list[float]]
    saved: list[MemoryFact]


class MemorySavePipeline:
    """In-process Phase 0 LangGraph pipeline for unstructured memory writes."""

    def __init__(
        self,
        *,
        store: SQLiteMemoryStore,
        extractor: FactExtractor,
        embedder: EmbeddingProvider,
    ) -> None:
        self.store = store
        self.extractor = extractor
        self.embedder = embedder
        self._graph = self._build_graph()

    def _build_graph(self) -> Any:
        graph = StateGraph(PipelineState)
        graph.add_node("classify", self._classify)
        graph.add_node("extract", self._extract)
        graph.add_node("dedup", self._dedup)
        graph.add_node("embed", self._embed)
        graph.add_node("store", self._store)
        graph.add_edge(START, "classify")
        graph.add_edge("classify", "extract")
        graph.add_edge("extract", "dedup")
        graph.add_edge("dedup", "embed")
        graph.add_edge("embed", "store")
        graph.add_edge("store", END)
        return graph.compile()

    def save_text(self, *, user_id: str, text: str) -> list[MemoryFact]:
        result = self._graph.invoke({"user_id": user_id, "text": text})
        return list(result.get("saved", []))

    def _classify(self, state: PipelineState) -> PipelineState:
        return {"should_store": bool(state["text"].strip())}

    def _extract(self, state: PipelineState) -> PipelineState:
        if not state.get("should_store", False):
            return {"extracted": []}
        return {
            "extracted": self.extractor.extract(
                text=state["text"],
                user_id=state["user_id"],
            )
        }

    def _dedup(self, state: PipelineState) -> PipelineState:
        existing = self.store.list_facts(state["user_id"])
        seen = {(fact.kind, fact.key.casefold(), fact.value.casefold()) for fact in existing}
        deduped: list[ExtractedFact] = []
        for fact in state.get("extracted", []):
            identity = (fact.kind, fact.key.casefold(), fact.value.casefold())
            if identity in seen:
                continue
            seen.add(identity)
            deduped.append(fact)
        return {"deduped": deduped}

    def _embed(self, state: PipelineState) -> PipelineState:
        facts = state.get("deduped", [])
        texts = [f"{fact.key}: {fact.value}" for fact in facts]
        embeddings = self.embedder.embed(texts)
        if len(embeddings) != len(facts):
            raise ValueError("embedding provider returned an unexpected number of vectors")
        return {"embeddings": embeddings}

    def _store(self, state: PipelineState) -> PipelineState:
        facts = state.get("deduped", [])
        embeddings = state.get("embeddings", [])
        saved: list[MemoryFact] = []
        for extracted, embedding in zip(facts, embeddings, strict=True):
            fact = MemoryFact(
                user_id=state["user_id"],
                key=extracted.key,
                value=extracted.value,
                kind=extracted.kind,
                importance=extracted.importance,
                embedding=embedding,
            )
            self.store.save_fact(fact)
            saved.append(fact)
        return {"saved": saved}
