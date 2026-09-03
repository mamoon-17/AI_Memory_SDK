from __future__ import annotations

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

from memory_sdk.client import Memory
from memory_sdk.config import MemoryConfig
from memory_sdk.models import MemoryFact


def _studio_url(path: str, *, user_id: str, query: str = "") -> str:
    params = {"user_id": user_id}
    if query:
        params["q"] = query
    return f"{path}?{urlencode(params)}"


def render_memory_table(
    facts: list[MemoryFact], *, user_id: str, query: str, users: list[str] | None = None
) -> str:
    users = users or ([user_id] if user_id else [])
    options = "".join(
        f'<option value="{escape(candidate)}"'
        f'{" selected" if candidate == user_id else ""}>{escape(candidate)}</option>'
        for candidate in users
    )
    if not options:
        options = '<option value="">No users found</option>'

    rows = "".join(
        "<tr>"
        f"<td>{escape(fact.kind)}</td>"
        f'<td><a href="{escape(_studio_url(f"/memories/{fact.id}", user_id=user_id, query=query))}">'
        f"{escape(fact.key)}</a></td>"
        f"<td>{escape(fact.value)}</td>"
        f"<td>{fact.importance:.2f}</td>"
        f"<td>{escape(fact.created_at.isoformat())}</td>"
        f"<td>{escape(fact.updated_at.isoformat())}</td>"
        "</tr>"
        for fact in facts
    )
    if not rows:
        rows = '<tr><td colspan="6">No memories found.</td></tr>'

    scope_text = (
        f'Local read-only inspection for user <strong>{escape(user_id)}</strong>.'
        if user_id
        else "No user scopes exist in this database yet."
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Memory Studio</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 1200px; padding: 0 1rem; }}
    form {{ display: flex; gap: .75rem; margin: 1rem 0 1.5rem; }}
    input, select {{ flex: 1; padding: .65rem .8rem; }}
    button {{ padding: .65rem 1rem; cursor: pointer; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: .65rem; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: white; }}
    .meta {{ color: #666; }}
    a {{ color: inherit; }}
  </style>
</head>
<body>
  <h1>Memory Studio</h1>
  <p class="meta">{scope_text}</p>
  <form method="get" action="/">
    <select name="user_id" aria-label="User scope">{options}</select>
    <input type="search" name="q" value="{escape(query)}" placeholder="Search key or value">
    <button type="submit">Inspect</button>
  </form>
  <table>
    <thead><tr><th>Kind</th><th>Key</th><th>Value</th><th>Importance</th><th>Created</th><th>Updated</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""


def render_memory_detail(fact: MemoryFact, *, query: str = "") -> str:
    back_url = _studio_url("/", user_id=fact.user_id, query=query)
    embedding = "present" if fact.embedding else "not stored"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(fact.key)} · Memory Studio</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
    dl {{ display: grid; grid-template-columns: 10rem 1fr; gap: .75rem 1rem; }}
    dt {{ font-weight: 700; }}
    dd {{ margin: 0; overflow-wrap: anywhere; }}
    .value {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <p><a href="{escape(back_url)}">← Back to memories</a></p>
  <h1>{escape(fact.key)}</h1>
  <dl>
    <dt>ID</dt><dd>{escape(fact.id)}</dd>
    <dt>User</dt><dd>{escape(fact.user_id)}</dd>
    <dt>Kind</dt><dd>{escape(fact.kind)}</dd>
    <dt>Value</dt><dd class="value">{escape(fact.value)}</dd>
    <dt>Importance</dt><dd>{fact.importance:.2f}</dd>
    <dt>Embedding</dt><dd>{embedding}</dd>
    <dt>Created</dt><dd>{escape(fact.created_at.isoformat())}</dd>
    <dt>Updated</dt><dd>{escape(fact.updated_at.isoformat())}</dd>
  </dl>
</body>
</html>"""


def create_handler(
    memory: Memory, *, initial_user_id: str | None, limit: int
) -> type[BaseHTTPRequestHandler]:
    class MemoryStudioHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            users = memory.store.list_user_ids()
            requested_user_id = params.get("user_id", [initial_user_id or ""])[0].strip()
            user_id = requested_user_id or (users[0] if users else "")
            query = params.get("q", [""])[0].strip()

            if parsed.path == "/":
                facts = (
                    memory.retrieve(user_id=user_id, query=query or None, limit=limit)
                    if user_id
                    else []
                )
                body = render_memory_table(
                    facts, user_id=user_id, query=query, users=users
                ).encode("utf-8")
                self._send_html(body)
                return

            if parsed.path.startswith("/memories/"):
                fact_id = parsed.path.removeprefix("/memories/")
                fact = memory.store.get_fact(user_id=user_id, fact_id=fact_id) if user_id else None
                if fact is None:
                    self.send_error(404)
                    return
                self._send_html(render_memory_detail(fact, query=query).encode("utf-8"))
                return

            self.send_error(404)

        def _send_html(self, body: bytes) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return MemoryStudioHandler


def serve(
    *,
    database_path: str,
    user_id: str | None = None,
    host: str = "127.0.0.1",
    port: int = 8765,
    limit: int = 100,
) -> None:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    memory = Memory(MemoryConfig(database_path=database_path))
    server = ThreadingHTTPServer(
        (host, port), create_handler(memory, initial_user_id=user_id, limit=limit)
    )
    scope = user_id or "auto-discover"
    print(f"Memory Studio: http://{host}:{port} (user={scope})")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local read-only Memory Studio")
    parser.add_argument("--db", default="memory.db", help="SQLite database path")
    parser.add_argument(
        "--user-id",
        help="Initial user scope to inspect (default: discover users from the local database)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: local-only)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    serve(database_path=args.db, user_id=args.user_id, host=args.host, port=args.port, limit=args.limit)


if __name__ == "__main__":
    main()
