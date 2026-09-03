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
