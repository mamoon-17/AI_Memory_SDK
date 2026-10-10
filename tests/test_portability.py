import json

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
