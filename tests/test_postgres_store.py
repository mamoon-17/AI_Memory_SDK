from __future__ import annotations

import os
from uuid import uuid4

import pytest
from memory_sdk import Memory, MemoryFact
from memory_sdk.storage.postgres import PostgresMemoryStore

DSN = os.environ.get("MEMORY_SDK_TEST_POSTGRES_DSN")
pytestmark = pytest.mark.skipif(not DSN, reason="Postgres integration DSN is not configured")


def test_postgres_store_crud_vector_search_and_memory_injection() -> None:
    assert DSN is not None
    store = PostgresMemoryStore(DSN)
    user_id = f"postgres-test-{uuid4()}"
    other_user_id = f"postgres-other-{uuid4()}"

    primary = MemoryFact(
        user_id=user_id,
        key="favorite_color",
        value="blue",
        importance=0.9,
        embedding=[1.0, 0.0, 0.0],
    )
    secondary = MemoryFact(
        user_id=user_id,
        key="favorite_food",
        value="pasta",
        importance=0.6,
        embedding=[0.0, 1.0, 0.0],
    )
    isolated = MemoryFact(
        user_id=other_user_id,
        key="favorite_color",
        value="green",
        embedding=[1.0, 0.0, 0.0],
    )

    store.save_fact(primary)
    store.save_fact(secondary)
    store.save_fact(isolated)

    assert [fact.id for fact in store.list_facts(user_id)] == [primary.id, secondary.id]
    assert store.get_fact(user_id=user_id, fact_id=primary.id) == primary
    assert store.get_fact(user_id=other_user_id, fact_id=primary.id) is None

    nearest = store.search_by_vector(user_id=user_id, query_vector=[1.0, 0.0, 0.0], limit=1)
    assert nearest is not None
    assert [fact.id for fact in nearest] == [primary.id]
    assert store.search_by_vector(user_id=user_id, query_vector=[1.0, 0.0], limit=1) is None

    memory = Memory(store=store)
    structured = memory.save(user_id=user_id, key="timezone", value="UTC+5")
    assert memory.retrieve(user_id=user_id, limit=10)
    assert memory.forget(user_id=other_user_id, memory_id=structured.id) is False
    assert memory.forget(user_id=user_id, memory_id=structured.id) is True

    assert store.delete_fact(primary.id) is True
    assert store.get_fact(user_id=user_id, fact_id=primary.id) is None
