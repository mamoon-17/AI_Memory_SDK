from memory_sdk.models import MemoryFact
from memory_sdk.storage.sqlite import SQLiteMemoryStore


def test_studio_storage_discovery_and_scoped_detail(tmp_path) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    alpha = MemoryFact(user_id="alpha", kind="fact", key="role", value="engineer")
    beta = MemoryFact(user_id="beta", kind="preference", key="theme", value="dark")
    store.save_fact(beta)
    store.save_fact(alpha)

    assert store.list_user_ids() == ["alpha", "beta"]
    assert store.get_fact(user_id="alpha", fact_id=alpha.id) == alpha
    assert store.get_fact(user_id="beta", fact_id=alpha.id) is None
    assert store.get_fact(user_id="alpha", fact_id="missing") is None
