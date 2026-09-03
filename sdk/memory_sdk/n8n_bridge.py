from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from memory_sdk.adapters import FastEmbedEmbeddingProvider
from memory_sdk.client import Memory
from memory_sdk.config import MemoryConfig


def _serialize_facts(facts: list[Any]) -> list[dict[str, Any]]:
    return [fact.model_dump(mode="json") for fact in facts]


def execute(
    payload: dict[str, Any], *, database_path: str, llm_model: str | None = None
) -> dict[str, Any]:
    operation = str(payload.get("operation", "")).strip().lower()
    user_id = str(payload.get("userId", "")).strip()
    if not operation:
        raise ValueError("operation is required")
    if not user_id:
        raise ValueError("userId is required")

    config = MemoryConfig(database_path=database_path, llm_model=llm_model)

    if operation == "save":
        text = str(payload.get("text", "")).strip()
        if text:
            memory = Memory(config)
            return {"memories": _serialize_facts(memory.save_text(user_id=user_id, text=text))}

        key = str(payload.get("key", "")).strip()
        value = str(payload.get("value", "")).strip()
        if not key or not value:
            raise ValueError("save requires text or both key and value")
        kind = str(payload.get("kind", "fact")).strip() or "fact"
        importance = float(payload.get("importance", 0.5))
        memory = Memory(config)
        fact = memory.save(
            user_id=user_id,
            key=key,
            value=value,
            kind=kind,
            importance=importance,
        )
        return {"memories": [fact.model_dump(mode="json")]}

    if operation == "retrieve":
        limit = int(payload.get("limit", 10))
        memory = Memory(config)
        return {"memories": _serialize_facts(memory.retrieve(user_id=user_id, limit=limit))}

    if operation == "search":
        query = str(payload.get("query", "")).strip()
        if not query:
            raise ValueError("search requires query")
        limit = int(payload.get("limit", 10))
        embedder = FastEmbedEmbeddingProvider(config.embedding_model)
        memory = Memory(config, embedder=embedder)
        return {
            "memories": _serialize_facts(
                memory.retrieve(user_id=user_id, query=query, limit=limit)
            )
        }

    if operation == "forget":
        memory_id = str(payload.get("memoryId", "")).strip()
        if not memory_id:
            raise ValueError("forget requires memoryId")
        memory = Memory(config)
        return {"forgotten": memory.forget(user_id=user_id, memory_id=memory_id)}

    raise ValueError(f"unsupported operation: {operation}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local JSON bridge for the n8n AI Memory SDK node")
    parser.add_argument("--db", default="./memory.db", help="Path to the local SQLite memory database")
    parser.add_argument("--llm-model", default=None, help="LiteLLM model used for unstructured Save")
    args = parser.parse_args()

    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise TypeError("bridge input must be a JSON object")
        result = execute(payload, database_path=args.db, llm_model=args.llm_model)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    json.dump(result, sys.stdout, separators=(",", ":"))
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
