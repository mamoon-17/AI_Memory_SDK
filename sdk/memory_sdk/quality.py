from __future__ import annotations

from datetime import UTC, datetime

from memory_sdk.providers import ExtractedFact

_KIND_PRIORS = {
    "identity": 0.9,
    "constraint": 0.9,
    "goal": 0.85,
    "preference": 0.8,
    "relationship": 0.75,
    "fact": 0.55,
    "event": 0.5,
    "transient": 0.25,
}


def score_importance(fact: ExtractedFact) -> float:
    """Deterministically combine extractor signal with durable-memory heuristics."""
    kind_prior = _KIND_PRIORS.get(fact.kind.casefold(), 0.5)
    specificity = _specificity_score(fact.value)
    score = (0.65 * fact.importance) + (0.25 * kind_prior) + (0.10 * specificity)
    return round(min(1.0, max(0.0, score)), 6)


def recency_score(updated_at: datetime, *, now: datetime | None = None, half_life_days: float = 30.0) -> float:
    """Return exponential recency decay with a configurable half-life."""
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    current = now or datetime.now(UTC)
    timestamp = updated_at if updated_at.tzinfo is not None else updated_at.replace(tzinfo=UTC)
    age_seconds = max(0.0, (current - timestamp).total_seconds())
    age_days = age_seconds / 86400.0
    return 0.5 ** (age_days / half_life_days)


def _specificity_score(value: str) -> float:
    words = [word for word in value.split() if word]
    if not words:
        return 0.0
    if len(words) == 1:
        return 0.45
    if len(words) <= 4:
        return 0.65
    if len(words) <= 12:
        return 0.8
    return 0.9
