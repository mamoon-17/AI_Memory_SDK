# AI Memory SDK TypeScript client

This package is intentionally thin. It does not implement extraction, conflict resolution, importance scoring, ranking, embeddings, or storage in TypeScript. Those semantics remain in the Python SDK.

The default transport invokes the local `memory-sdk-bridge` executable and speaks the same JSON protocol used by the n8n integration.

```ts
import { MemoryClient, ProcessBridgeTransport } from 'ai-memory-sdk-client';

const memory = new MemoryClient(
  new ProcessBridgeTransport({ databasePath: './memory.db' }),
);

await memory.save({
  userId: 'user-123',
  key: 'favorite_language',
  value: 'TypeScript',
  kind: 'preference',
});

const recent = await memory.retrieve('user-123', { limit: 10 });
const matches = await memory.search({
  userId: 'user-123',
  query: 'language preference',
  limit: 5,
});
await memory.forget({ userId: 'user-123', memoryId: recent[0].id });
```

For text Save, configure a LiteLLM model on `ProcessBridgeTransport` and pass `{ userId, text }` to `save()`. Search still uses the Python SDK's local FastEmbed path.

Custom transports can implement the exported `MemoryTransport` interface when an application needs a different process or IPC boundary while preserving the same bridge request/response protocol.
# Process reliability and offline search

`ProcessBridgeTransport` uses asynchronous process execution. Defaults are a 30 second
timeout and 1 MiB per output stream. Override `timeoutMs` and `maxBufferBytes` with
positive safe integers. A timed-out process is killed; its write may already have
committed. Inspect state before retrying saves. There are no automatic retries.

`BridgeError.code` distinguishes `TIMEOUT`, `OUTPUT_LIMIT`, `PROCESS` and `PROTOCOL`.
The original error is retained in `cause`; it can contain sensitive process details.
Use `bridgeArgs` to invoke an interpreter, for example `bridgeCommand: 'python'` and
`bridgeArgs: ['-m', 'memory_sdk.n8n_bridge']`. Arguments bypass a shell. On Windows,
use a native executable rather than a `.cmd` wrapper.

```ts
const matches = await memory.search({
  userId: 'alice', query: 'Python', mode: 'lexical',
  filters: { kind: 'preference', min_importance: 0.5 },
});
```

Semantic search remains the default. Lexical mode avoids constructing FastEmbed and
does not download model weights. `retrieve` also accepts `filters`; filter field names
match Python (`kind`, `key`, `min_importance`, `updated_after`), with aware ISO timestamps.
Python owns ranking and validation. Listing, portability and bulk forgetting currently
belong to the Python API; the TypeScript bridge retains its four-operation contract.

