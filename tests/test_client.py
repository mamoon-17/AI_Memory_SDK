from memory_sdk import Memory, MemoryConfig


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


def test_retrieve_rejects_non_positive_limit(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / "memory.db"))

    try:
        memory.retrieve(user_id="alice", limit=0)
    except ValueError as exc:
        assert str(exc) == "limit must be at least 1"
    else:
        raise AssertionError("expected ValueError")
