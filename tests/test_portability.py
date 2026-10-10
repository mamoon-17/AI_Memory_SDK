import json
import pytest

from memory_sdk import Memory, MemoryConfig


def test_export_is_complete_and_scoped(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    for i in range(15):
        memory.save(user_id='alice', key=str(i), value='café')
    memory.save(user_id='bob', key='secret', value='hidden')
    payload = json.loads(memory.export_json(user_id='alice'))
    assert payload['schema_version'] == 1
    assert len(payload['memories']) == 15
    assert all(f['user_id'] == 'alice' and 'embedding' not in f for f in payload['memories'])
    assert 'café' in memory.export_json(user_id='alice')


def test_export_vectors_are_opt_in(tmp_path):
    from memory_sdk import MemoryFact

    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    memory.save_many([MemoryFact(user_id='alice', key='a', value='b', embedding=[1.0, 0.0])])
    payload = json.loads(memory.export_json(user_id='alice', include_embeddings=True))
    assert payload['memories'][0]['embedding'] == [1.0, 0.0]


def test_import_roundtrip_is_repeatable(tmp_path):
    source = Memory(MemoryConfig(database_path=tmp_path / 'source.db'))
    source.save(user_id='alice', key='language', value='Python')
    target = Memory(MemoryConfig(database_path=tmp_path / 'target.db'))
    data = source.export_json(user_id='alice')
    target.import_json(user_id='alice', data=data)
    target.import_json(user_id='alice', data=data)
    assert target.list(user_id='alice') == source.list(user_id='alice')


def test_import_rejects_cross_scope_id_without_partial_writes(tmp_path):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    bob = memory.save(user_id='bob', key='secret', value='private')
    payload = {'schema_version': 1, 'user_id': 'alice', 'memories': [
        dict(user_id='alice', key='valid', value='first'),
        dict(id=bob.id, user_id='alice', key='bad', value='overwrite'),
    ]}
    with pytest.raises(ValueError, match='another user'):
        memory.import_json(user_id='alice', data=json.dumps(payload))
    assert memory.list(user_id='alice') == []
    assert memory.list(user_id='bob') == [bob]


@pytest.mark.parametrize('changes', [
    {'schema_version': 2}, {'user_id': 'bob'}, {'memories': {}},
    {'memories': [dict(user_id='bob', key='a', value='b')]},
])
def test_import_rejects_invalid_envelope(tmp_path, changes):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    payload = {'schema_version': 1, 'user_id': 'alice', 'memories': []} | changes
    with pytest.raises(ValueError):
        memory.import_json(user_id='alice', data=json.dumps(payload))
