from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryFact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    kind: str = "fact"
    key: str
    value: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    embedding: list[float] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
