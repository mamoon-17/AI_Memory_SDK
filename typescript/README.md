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
