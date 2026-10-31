from memory_sdk import MemoryFact, SQLiteMemoryStore


def test_sqlite_update_preserves_row_identity(tmp_path):
    store = SQLiteMemoryStore(tmp_path / 'memory.db')
    fact = MemoryFact(user_id='alice', key='language', value='Python', embedding=[1.0, 0.0])
    store.save_fact(fact)
    with store._transaction() as connection:
        before = connection.execute('SELECT rowid FROM memory_facts WHERE id = ?', (fact.id,)).fetchone()[0]
    for value in ['Rust', 'Go', 'Python']:
        fact = fact.model_copy(update={'value': value})
        store.save_fact(fact)
    with store._transaction() as connection:
        after = connection.execute('SELECT rowid FROM memory_facts WHERE id = ?', (fact.id,)).fetchone()[0]
        count = connection.execute('SELECT count(*) FROM memory_fact_vectors').fetchone()[0]
    assert after == before
    assert count == 1
    assert store.list_facts('alice') == [fact]
    assert store.search_by_vector(user_id='alice', query_vector=[1.0, 0.0], limit=1) == [fact]
