from __future__ import annotations

import json
import subprocess
import sys

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


def _run_bridge(database_path: str, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "memory_sdk.n8n_bridge", "--db", database_path],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def test_bridge_process_round_trip(tmp_path) -> None:
    database_path = str(tmp_path / "memory.db")
    saved = _run_bridge(
        database_path,
        {"operation": "save", "userId": "alice", "key": "editor", "value": "VS Code"},
    )
    assert saved.returncode == 0, saved.stderr
    memory_id = json.loads(saved.stdout)["memories"][0]["id"]

    retrieved = _run_bridge(
        database_path,
        {"operation": "retrieve", "userId": "alice", "limit": 10},
    )
    assert retrieved.returncode == 0, retrieved.stderr
    assert json.loads(retrieved.stdout)["memories"][0]["id"] == memory_id


def test_bridge_process_reports_invalid_input(tmp_path) -> None:
    result = _run_bridge(str(tmp_path / "memory.db"), {"operation": "retrieve"})
    assert result.returncode == 1
    assert "userId is required" in result.stderr
