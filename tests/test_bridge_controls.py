import pytest
from memory_sdk.n8n_bridge import execute


def test_lexical_search_is_offline_filtered_and_scoped(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('lexical operations must not construct an embedder')

    monkeypatch.setattr('memory_sdk.n8n_bridge.FastEmbedEmbeddingProvider', forbidden)
    db = str(tmp_path / 'memory.db')
    for user, kind in [('alice', 'fact'), ('alice', 'preference'), ('bob', 'preference')]:
        execute({'operation': 'save', 'userId': user, 'kind': kind, 'key': 'language', 'value': 'Python'},
                database_path=db)
    result = execute({'operation': 'search', 'userId': 'alice', 'query': 'python', 'mode': 'lexical',
                          'filters': {'kind': 'preference'}}, database_path=db)
    assert len(result['memories']) == 1
    assert result['memories'][0]['kind'] == 'preference'
    assert result['memories'][0]['user_id'] == 'alice'


@pytest.mark.parametrize('user_id', [None, 42, [], {}])
def test_bridge_rejects_nonstring_scopes(tmp_path, user_id):
    with pytest.raises(TypeError, match='string'):
        execute({'operation': 'retrieve', 'userId': user_id}, database_path=str(tmp_path / 'm.db'))
