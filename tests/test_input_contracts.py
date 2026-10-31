import pytest

from memory_sdk.n8n_bridge import execute


@pytest.mark.parametrize('limit', [True, False, 1.9, '2', None, [], {}])
@pytest.mark.parametrize('operation', ['retrieve', 'search'])
def test_bridge_rejects_noninteger_limits_before_opening_store(tmp_path, limit, operation):
    database = tmp_path / 'uncreated.db'
    with pytest.raises(TypeError, match='integer'):
        execute({'operation': operation, 'userId': 'alice', 'query': 'x', 'limit': limit},
                database_path=str(database))
    assert not database.exists()


@pytest.mark.parametrize('limit', [0, -1])
def test_bridge_rejects_nonpositive_limits(tmp_path, limit):
    database = tmp_path / 'uncreated.db'
    with pytest.raises(ValueError, match='at least 1'):
        execute({'operation': 'retrieve', 'userId': 'alice', 'limit': limit},
                database_path=str(database))
    assert not database.exists()
