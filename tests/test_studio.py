from datetime import UTC, datetime

from memory_sdk.models import MemoryFact
from memory_sdk.studio import render_memory_detail, render_memory_table


def _fact(*, user_id: str = "user-1", key: str = "theme", value: str = "<dark>") -> MemoryFact:
    return MemoryFact(
        user_id=user_id,
        kind="preference",
        key=key,
        value=value,
        importance=0.9,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, tzinfo=UTC),
    )


def test_render_memory_table_escapes_content_and_shows_metadata() -> None:
    fact = _fact()

    html = render_memory_table(
        [fact], user_id="user-1", query="theme", users=["other", "user-1"]
    )

    assert "Memory Studio" in html
    assert "preference" in html
    assert "theme" in html
    assert "&lt;dark&gt;" in html
    assert "<dark>" not in html
    assert "0.90" in html
    assert "2026-01-01T00:00:00+00:00" in html
    assert "2026-01-02T00:00:00+00:00" in html
    assert 'value="user-1" selected' in html
    assert f"/memories/{fact.id}?user_id=user-1&amp;q=theme" in html


def test_render_memory_table_has_empty_state() -> None:
    html = render_memory_table([], user_id="user-1", query="missing")

    assert "No memories found." in html
    assert 'value="missing"' in html


def test_render_memory_table_handles_database_with_no_users() -> None:
    html = render_memory_table([], user_id="", query="", users=[])

    assert "No users found" in html
    assert "No user scopes exist in this database yet." in html


def test_render_memory_detail_is_scoped_and_escaped() -> None:
    fact = _fact(value="<script>alert(1)</script>")

    html = render_memory_detail(fact, query="theme")

    assert fact.id in html
    assert "user-1" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>" not in html
    assert "Embedding" in html
    assert "not stored" in html
    assert "/?user_id=user-1&amp;q=theme" in html
