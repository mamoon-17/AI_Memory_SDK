from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class MemoryFact(BaseModel):
    @field_validator("id", "user_id", "kind", "key", "value")
    @classmethod
    def require_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("embedding")
    @classmethod
    def valid_embedding(cls, value: list[float] | None) -> list[float] | None:
        from math import isfinite

        if value is not None and (not value or not all(isfinite(v) for v in value)):
            raise ValueError("embedding must contain finite numbers and must not be empty")
        return value

    @field_validator("created_at", "updated_at")
    @classmethod
    def aware_timestamp(cls, value: datetime) -> datetime:
        if value.utcoffset() is None:
            raise ValueError("timestamps must include a timezone")
        return value

    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    kind: str = "fact"
    key: str
    value: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    embedding: list[float] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
