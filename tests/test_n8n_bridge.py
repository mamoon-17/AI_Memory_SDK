from __future__ import annotations

from memory_sdk.client import Memory
from memory_sdk.config import MemoryConfig
from memory_sdk.n8n_bridge import execute


def test_forget_is_user_scoped(tmp_path) -> None:
    database_path = tmp_path / "memory.db"
    memory = Memory(MemoryConfig(database_path=database_path))
    fact = memory.save(user_id="alice", key="city", value="Lahore")

    assert memory.forget(user_id="bob", memory_id=fact.id) is False
    assert memory.store.get_fact(user_id="alice", fact_id=fact.id) is not None

    assert memory.forget(user_id="alice", memory_id=fact.id) is True
    assert memory.store.get_fact(user_id="alice", fact_id=fact.id) is None


def test_bridge_structured_save_retrieve_and_forget(tmp_path) -> None:
    database_path = str(tmp_path / "memory.db")

    saved = execute(
        {
            "operation": "save",
            "userId": "alice",
            "key": "language",
            "value": "Python",
            "kind": "preference",
            "importance": 0.8,
        },
        database_path=database_path,
    )
    memory_id = saved["memories"][0]["id"]

    retrieved = execute(
        {"operation": "retrieve", "userId": "alice", "limit": 10},
        database_path=database_path,
    )
    assert [item["id"] for item in retrieved["memories"]] == [memory_id]

    forgotten = execute(
        {"operation": "forget", "userId": "alice", "memoryId": memory_id},
        database_path=database_path,
    )
    assert forgotten == {"forgotten": True}

    retrieved_after = execute(
        {"operation": "retrieve", "userId": "alice", "limit": 10},
        database_path=database_path,
    )
    assert retrieved_after == {"memories": []}


def test_bridge_rejects_cross_user_forget(tmp_path) -> None:
    database_path = str(tmp_path / "memory.db")
    saved = execute(
        {"operation": "save", "userId": "alice", "key": "city", "value": "Lahore"},
        database_path=database_path,
    )
    memory_id = saved["memories"][0]["id"]

    result = execute(
        {"operation": "forget", "userId": "bob", "memoryId": memory_id},
        database_path=database_path,
    )
    assert result == {"forgotten": False}
