from datetime import UTC, datetime

from memory_sdk.models import MemoryFact
from memory_sdk.studio import render_memory_table


def test_render_memory_table_escapes_content_and_shows_metadata() -> None:
    fact = MemoryFact(
        user_id="user-1",
        kind="preference",
        key="theme",
        value="<dark>",
        importance=0.9,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 2, tzinfo=UTC),
    )

    html = render_memory_table([fact], user_id="user-1", query="theme")

    assert "Memory Studio" in html
    assert "preference" in html
    assert "theme" in html
    assert "&lt;dark&gt;" in html
    assert "<dark>" not in html
    assert "0.90" in html
    assert "2026-01-01T00:00:00+00:00" in html
    assert "2026-01-02T00:00:00+00:00" in html


def test_render_memory_table_has_empty_state() -> None:
    html = render_memory_table([], user_id="user-1", query="missing")

    assert "No memories found." in html
    assert 'value="missing"' in html
