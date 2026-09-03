import memory_sdk.storage.sqlite as sqlite_store_module
from memory_sdk.models import MemoryFact
from memory_sdk.storage.sqlite import SQLiteMemoryStore


def test_sqlite_store_round_trip(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    fact = MemoryFact(user_id="user-1", key="favorite_color", value="blue")

    store.save_fact(fact)
    facts = store.list_facts("user-1")

    assert len(facts) == 1
    assert facts[0].id == fact.id
    assert facts[0].key == "favorite_color"
    assert facts[0].value == "blue"


def test_sqlite_store_scopes_by_user(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    store.save_fact(MemoryFact(user_id="user-a", key="city", value="Tashkent"))
    store.save_fact(MemoryFact(user_id="user-b", key="city", value="Lahore"))

    facts = store.list_facts("user-a")

    assert [fact.value for fact in facts] == ["Tashkent"]


def test_sqlite_vec_search_is_user_scoped(tmp_path):
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    near = MemoryFact(
        user_id="user-a",
        key="city",
        value="Tashkent",
        embedding=[1.0, 0.0],
    )
    far = MemoryFact(
        user_id="user-a",
        key="food",
        value="pasta",
        embedding=[0.0, 1.0],
    )
    other_user = MemoryFact(
        user_id="user-b",
        key="city",
        value="Lahore",
        embedding=[1.0, 0.0],
    )

    store.save_fact(near)
    store.save_fact(far)
    store.save_fact(other_user)

    results = store.search_by_vector(user_id="user-a", query_vector=[1.0, 0.0], limit=2)

    assert results is not None
    assert [fact.id for fact in results] == [near.id, far.id]


def test_sqlite_vec_backfills_after_extension_becomes_available(tmp_path, monkeypatch):
    original_loader = sqlite_store_module._load_sqlite_vec

    def unavailable(_connection):
        return None

    monkeypatch.setattr(sqlite_store_module, "_load_sqlite_vec", unavailable)
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    fact = MemoryFact(
        user_id="user-a",
        key="language",
        value="Python",
        embedding=[1.0, 0.0],
    )
    store.save_fact(fact)
    assert store.search_by_vector(user_id="user-a", query_vector=[1.0, 0.0], limit=1) is None

    monkeypatch.setattr(sqlite_store_module, "_load_sqlite_vec", original_loader)
    results = store.search_by_vector(user_id="user-a", query_vector=[1.0, 0.0], limit=1)

    assert results is not None
    assert [result.id for result in results] == [fact.id]
