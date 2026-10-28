from datetime import timedelta

import pytest
from memory_sdk.filters import MemoryFilter
from memory_sdk.models import MemoryFact
from pydantic import ValidationError


def test_filter_combines_exact_fields_importance_and_time():
    fact = MemoryFact(user_id='alice', key='Editor', value='vim', kind='preference')
    assert MemoryFilter(kind='preference', min_importance=0.5).matches(fact)
    assert not MemoryFilter(key='editor').matches(fact)
    assert not MemoryFilter(updated_after=fact.updated_at).matches(fact)
    assert MemoryFilter(updated_after=fact.updated_at - timedelta(seconds=1)).matches(fact)
    assert not MemoryFilter(min_importance=0.6).matches(fact)


def test_filter_rejects_unknown_fields_and_naive_time():
    with pytest.raises(ValidationError):
        MemoryFilter(typo='x')
    with pytest.raises(ValidationError):
        MemoryFilter(updated_after='2026-10-09T00:00:00')
