import sqlite3

import pytest
from memory_sdk import MemoryFact, SQLiteMemoryStore


def test_sqlite_transactions_close_even_after_errors(tmp_path, monkeypatch):
    opened, closed = [], []
    original = sqlite3.connect

    class TrackedConnection(sqlite3.Connection):
        def close(self):
            closed.append(id(self))
            super().close()

    def connect(*args, **kwargs):
        connection = original(*args, factory=TrackedConnection, **kwargs)
        opened.append(id(connection))
        return connection

    monkeypatch.setattr(sqlite3, 'connect', connect)
    store = SQLiteMemoryStore(tmp_path / 'memory.db')
    fact = MemoryFact(user_id='alice', key='a', value='b')
    store.save_fact(fact)
    assert store.list_facts('alice') == [fact]
    assert store.get_fact(user_id='alice', fact_id=fact.id) == fact
    store.list_user_ids()
    with pytest.raises(sqlite3.Error), store._transaction() as connection:
        connection.execute('invalid sql')
    store.delete_fact(fact.id)
    assert sorted(opened) == sorted(closed)
