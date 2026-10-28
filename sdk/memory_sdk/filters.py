"""Storage-independent exact filters; applied before ranking and limiting."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from memory_sdk.models import MemoryFact


class MemoryFilter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: str | None = None
    key: str | None = None
    min_importance: float = Field(default=0.0, ge=0.0, le=1.0)
    updated_after: datetime | None = None

    @field_validator("updated_after")
    @classmethod
    def aware_time(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.utcoffset() is None:
            raise ValueError("updated_after must include a timezone")
        return value

    def matches(self, fact: MemoryFact) -> bool:
        return (
            (self.kind is None or fact.kind == self.kind)
            and (self.key is None or fact.key == self.key)
            and fact.importance >= self.min_importance
            and (self.updated_after is None or fact.updated_at > self.updated_after)
        )
