# Filters and portable records

```python
from memory_sdk import Memory, MemoryFilter

memory = Memory()
memory.save(user_id="alice", key="editor", value="vim", kind="preference")
matches = memory.retrieve(user_id="alice", query="vim", limit=5,
                          filters=MemoryFilter(kind="preference", min_importance=0.4))
all_records = memory.list(user_id="alice")
backup = memory.export_json(user_id="alice")
```

Filters combine with AND, compare kind/key exactly, include the importance threshold,
and treat `updated_after` as strictly greater than an aware timestamp. Filtering occurs
before limiting; filtered vector search uses the complete user scope for correctness.
`list` has no relevance limit and sorts by creation time then ID.

`export_json` emits schema version 1 and omits vectors by default. Use
`include_embeddings=True` to preserve them. Without vectors a restored record uses
lexical fallback until re-embedded. Exports contain private plaintext; choose storage
and access permissions appropriate for your application.

Restore with `memory.import_json(user_id="alice", data=backup)`. Every record and the
envelope must match the requested scope. Identical existing records are skipped;
different content with an existing ID, duplicate IDs, invalid versions and cross-user
ID collisions are rejected before writes. Backend errors can leave partial writes;
imports are not a concurrent transaction and require exclusive application access.

Validation now rejects blank identifiers/content, empty or nonfinite vectors, and
naive timestamps. Existing databases containing these values need cleanup first.
