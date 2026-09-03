from datetime import UTC, datetime, timedelta

import pytest
from memory_sdk import ExtractedFact
from memory_sdk.quality import recency_score, score_importance


def test_importance_scoring_is_deterministic_and_kind_sensitive():
    preference = ExtractedFact(key="theme", value="dark mode", kind="preference", importance=0.5)
    transient = ExtractedFact(key="status", value="busy", kind="transient", importance=0.5)

    first = score_importance(preference)
    second = score_importance(preference)

    assert first == second
    assert first > score_importance(transient)
    assert 0.0 <= first <= 1.0


def test_recency_score_uses_thirty_day_half_life():
    now = datetime(2026, 9, 3, tzinfo=UTC)

    assert recency_score(now, now=now) == 1.0
    assert recency_score(now - timedelta(days=30), now=now) == pytest.approx(0.5)
    assert recency_score(now - timedelta(days=60), now=now) == pytest.approx(0.25)


def test_recency_score_rejects_non_positive_half_life():
    with pytest.raises(ValueError, match="half_life_days must be positive"):
        recency_score(datetime.now(UTC), half_life_days=0)
