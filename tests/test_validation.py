import pytest
from pydantic import ValidationError

from memory_sdk import MemoryFact


@pytest.mark.parametrize('field', ['id', 'user_id', 'kind', 'key', 'value'])
def test_blank_record_fields_are_rejected(field):
    payload = dict(user_id='alice', key='editor', value='vim')
    payload[field] = '  '
    with pytest.raises(ValidationError):
        MemoryFact(**payload)


@pytest.mark.parametrize('embedding', [[], [float('nan')], [float('inf')]])
def test_invalid_vectors_are_rejected(embedding):
    with pytest.raises(ValidationError):
        MemoryFact(user_id='alice', key='editor', value='vim', embedding=embedding)


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValidationError):
        MemoryFact(user_id='alice', key='editor', value='vim', created_at='2026-10-09T10:00:00')
