from __future__ import annotations

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from memory_sdk.client import Memory
from memory_sdk.config import MemoryConfig
from memory_sdk.models import MemoryFact


def render_memory_table(facts: list[MemoryFact], *, user_id: str, query: str) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{escape(fact.kind)}</td>"
        f"<td>{escape(fact.key)}</td>"
        f"<td>{escape(fact.value)}</td>"
        f"<td>{fact.importance:.2f}</td>"
        f"<td>{escape(fact.created_at.isoformat())}</td>"
        f"<td>{escape(fact.updated_at.isoformat())}</td>"
        "</tr>"
        for fact in facts
    )
    if not rows:
        rows = '<tr><td colspan="6">No memories found.</td></tr>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Memory Studio</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 1200px; padding: 0 1rem; }}
    form {{ display: flex; gap: .75rem; margin: 1rem 0 1.5rem; }}
    input {{ flex: 1; padding: .65rem .8rem; }}
    button {{ padding: .65rem 1rem; cursor: pointer; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: .65rem; text-align: left; vertical-align: top; }}
    th {{ position: sticky; top: 0; background: white; }}
    .meta {{ color: #666; }}
  </style>
</head>
<body>
  <h1>Memory Studio</h1>
  <p class="meta">Local read-only inspection for user <strong>{escape(user_id)}</strong>.</p>
  <form method="get" action="/">
    <input type="search" name="q" value="{escape(query)}" placeholder="Search key or value">
    <button type="submit">Search</button>
  </form>
  <table>
    <thead><tr><th>Kind</th><th>Key</th><th>Value</th><th>Importance</th><th>Created</th><th>Updated</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body>
</html>"""


def create_handler(memory: Memory, *, user_id: str, limit: int) -> type[BaseHTTPRequestHandler]:
    class MemoryStudioHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/":
                self.send_error(404)
                return

            query = parse_qs(parsed.query).get("q", [""])[0].strip()
            facts = memory.retrieve(user_id=user_id, query=query or None, limit=limit)
            body = render_memory_table(facts, user_id=user_id, query=query).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return MemoryStudioHandler


def serve(*, database_path: str, user_id: str, host: str = "127.0.0.1", port: int = 8765, limit: int = 100) -> None:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    memory = Memory(MemoryConfig(database_path=database_path))
    server = ThreadingHTTPServer((host, port), create_handler(memory, user_id=user_id, limit=limit))
    print(f"Memory Studio: http://{host}:{port} (user={user_id})")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local read-only Memory Studio")
    parser.add_argument("--db", default="memory.db", help="SQLite database path")
    parser.add_argument("--user-id", required=True, help="User scope to inspect")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: local-only)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    serve(database_path=args.db, user_id=args.user_id, host=args.host, port=args.port, limit=args.limit)


if __name__ == "__main__":
    main()
