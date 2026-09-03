from datetime import UTC, datetime, timedelta

from memory_sdk import Memory, MemoryConfig, MemoryFact


def test_save_and_retrieve_are_user_scoped(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / "memory.db"))

    memory.save(user_id="alice", key="favorite_editor", value="Neovim")
    memory.save(user_id="bob", key="favorite_editor", value="VS Code")

    results = memory.retrieve(user_id="alice")

    assert len(results) == 1
    assert results[0].user_id == "alice"
    assert results[0].value == "Neovim"


def test_retrieve_ranks_lexical_matches(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / "memory.db"))

    memory.save(user_id="alice", key="language", value="Python", importance=0.4)
    memory.save(user_id="alice", key="framework", value="FastAPI for Python services", importance=0.8)
    memory.save(user_id="alice", key="editor", value="Neovim", importance=1.0)

    results = memory.retrieve(user_id="alice", query="python", limit=2)

    assert [fact.key for fact in results] == ["framework", "language"]


def test_retrieve_without_query_balances_importance_and_time_decay(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / "memory.db"))
    now = datetime.now(UTC)
    durable = MemoryFact(
        user_id="alice",
        key="accessibility",
        value="requires screen reader support",
        importance=1.0,
        created_at=now - timedelta(days=45),
        updated_at=now - timedelta(days=45),
    )
    trivial = MemoryFact(
        user_id="alice",
        key="snack",
        value="had crackers",
        importance=0.1,
        created_at=now,
        updated_at=now,
    )
    memory.save_many([durable, trivial])

    results = memory.retrieve(user_id="alice", limit=2)

    assert [fact.key for fact in results] == ["accessibility", "snack"]


def test_retrieve_rejects_non_positive_limit(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / "memory.db"))

    try:
        memory.retrieve(user_id="alice", limit=0)
    except ValueError as exc:
        assert str(exc) == "limit must be at least 1"
    else:
        raise AssertionError("expected ValueError")
