from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field


class ExtractedFact(BaseModel):
    """Provider-neutral fact produced from unstructured input."""

    key: str
    value: str
    kind: str = "fact"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class FactExtractor(Protocol):
    def extract(self, *, text: str, user_id: str) -> list[ExtractedFact]: ...


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
