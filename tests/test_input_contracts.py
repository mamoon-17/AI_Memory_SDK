import pytest
from memory_sdk import Memory, MemoryConfig
from memory_sdk.n8n_bridge import execute


@pytest.mark.parametrize('limit', [True, False, 1.9, '2', None, [], {}])
@pytest.mark.parametrize('operation', ['retrieve', 'search'])
def test_bridge_rejects_noninteger_limits_before_opening_store(tmp_path, limit, operation):
    database = tmp_path / 'uncreated.db'
    with pytest.raises(TypeError, match='integer'):
        execute({'operation': operation, 'userId': 'alice', 'query': 'x', 'limit': limit},
                database_path=str(database))
    assert not database.exists()


@pytest.mark.parametrize('user_id,error', [('', ValueError), ('  ', ValueError), (None, TypeError)])
def test_sdk_rejects_invalid_scopes_before_provider_work(tmp_path, user_id, error):
    class ForbiddenProvider:
        def embed(self, texts):
            raise AssertionError('embedder must not run')

        def extract(self, **kwargs):
            raise AssertionError('extractor must not run')

    provider = ForbiddenProvider()
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'),
                    embedder=provider, extractor=provider)
    for operation in [
        lambda: memory.save(user_id=user_id, key='a', value='b'),
        lambda: memory.save_text(user_id=user_id, text='private message'),
        lambda: memory.retrieve(user_id=user_id, query='private query'),
        lambda: memory.list(user_id=user_id),
        lambda: memory.forget(user_id=user_id, memory_id='a'),
        lambda: memory.import_json(user_id=user_id, data='{}'),
    ]:
        with pytest.raises(error):
            operation()


@pytest.mark.parametrize('limit', [True, 1.5, '2', None])
def test_sdk_requires_integer_retrieval_limit(tmp_path, limit):
    memory = Memory(MemoryConfig(database_path=tmp_path / 'memory.db'))
    with pytest.raises(TypeError, match='integer'):
        memory.retrieve(user_id='alice', limit=limit)


@pytest.mark.parametrize('limit', [0, -1])
def test_bridge_rejects_nonpositive_limits(tmp_path, limit):
    database = tmp_path / 'uncreated.db'
    with pytest.raises(ValueError, match='at least 1'):
        execute({'operation': 'retrieve', 'userId': 'alice', 'limit': limit},
                database_path=str(database))
    assert not database.exists()
