from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """Runtime configuration for the local-first SDK profile."""

    database_path: Path = Field(default=Path("./memory.db"))
    embedding_provider: str = Field(default="local")
    embedding_model: str | None = Field(default=None)
    llm_provider: str | None = Field(default=None)
    llm_model: str | None = Field(default=None)
