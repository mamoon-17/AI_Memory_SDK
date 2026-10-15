# Async use and privacy boundaries

```python
import asyncio
from memory_sdk import AsyncMemory, MemoryFilter

async def main():
    async with AsyncMemory() as memory:
        await memory.save(user_id="alice", key="language", value="Python")
        facts = await memory.retrieve(user_id="alice", query="Python")
        print(facts)
        count = await memory.forget_all(user_id="alice", filters=MemoryFilter(key="language"))
        print(count)

asyncio.run(main())
```

Each async client owns one serial worker. Storage, extraction and embeddings execute
off the event loop; the constructor still initializes the store synchronously.
Use one client per application lifetime, and the async context manager or `aclose()`
to drain pending work. Injected stores/providers must permit use from the worker.
Do not call the underlying synchronous client concurrently yourself.

Cancelling an await does not stop a running worker or undo a write. A timeout is
therefore not evidence that a save failed; inspect the scope before retrying.
`aclose()` waits for running work, including a slow provider. Configure provider-level
timeouts for remote extraction. There are no hidden automatic mutation retries.

Structured save, listing, lexical retrieval, JSON export/import and forgetting need
no model or API key. `save_text` calls the configured extractor; LiteLLM may send
message text to a remote provider. FastEmbed can download weights on first use.
Local storage alone does not guarantee offline extraction or encryption at rest.

`forget_all` requires an explicit nonblank user ID and accepts the same exact filters.
It returns the number actually deleted; concurrent changes are not a snapshot.
Deleting records does not securely erase SQLite free pages, backups, WAL files or
existing JSON exports. Applications must manage those copies separately.

User IDs partition records, but are not authentication. A service wrapping this SDK
must derive the allowed scope from the authenticated caller. Studio is a trusted
local inspection tool and should stay bound to loopback.
