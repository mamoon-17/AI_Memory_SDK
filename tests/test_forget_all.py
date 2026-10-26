import pytest
from memory_sdk import Memory, MemoryConfig, MemoryFilter


def test_bulk_forget_preserves_other_scopes_and_unmatched_records(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    memory.save(user_id='alice', key='editor', value='vim', kind='preference')
    retained = memory.save(user_id='alice', key='city', value='Lahore')
    bob = memory.save(user_id='bob', key='editor', value='code', kind='preference')
    assert memory.forget_all(user_id='alice', filters=MemoryFilter(kind='preference')) == 1
    assert memory.list(user_id='alice') == [retained]
    assert memory.list(user_id='bob') == [bob]
    assert memory.forget_all(user_id='alice') == 1
    assert memory.forget_all(user_id='alice') == 0
    with pytest.raises(ValueError):
        memory.forget_all(user_id=' ')
