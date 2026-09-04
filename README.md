# AI Memory SDK

A local-first, zero-recurring-cost long-term memory engine for AI agents and n8n workflows.

## v1 principles

- Python SDK first.
- SQLite + sqlite-vec by default.
- Local ONNX embeddings via FastEmbed.
- Provider-agnostic fact extraction through LiteLLM.
- LangGraph runs in-process for orchestration.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
- Memory Studio is a local web UI.
- n8n distribution exposes Save, Retrieve, Search, and Forget operations.

## Local vector search

The default Python install includes `sqlite-vec`. The SDK loads the extension only when an embedding needs to be indexed or searched, creates the vector table lazily using the embedding dimension, and performs user-scoped KNN queries inside SQLite.

If the host Python/SQLite build cannot load extensions, facts and embeddings are still persisted normally. Retrieval safely falls back to in-process cosine ranking and then lexical ranking instead of making the local SDK unusable. Python builds with loadable SQLite extensions are therefore recommended for the default accelerated path.

## Optional Postgres + pgvector storage

SQLite + sqlite-vec remains the default local-first storage profile. For a shared Standard-tier deployment, install the optional PostgreSQL dependency and point the SDK at a PostgreSQL database with the `vector` extension available:

```bash
pip install 'ai-memory-sdk[postgres]'
```

Create a `PostgresMemoryStore` with a normal psycopg connection string and inject it into `Memory`:

```python
from memory_sdk import Memory, PostgresMemoryStore

store = PostgresMemoryStore(
    "postgresql://memory:memory@localhost:5432/memory"
)
memory = Memory(store=store)

memory.save(
    user_id="user-123",
    key="favorite_language",
    value="Python",
)

facts = memory.retrieve(user_id="user-123")
```

The adapter initializes its tables and enables the `vector` extension when the database role has permission to do so. Embeddings are retained on the fact row for fallback ranking, while pgvector-backed user-scoped cosine KNN is used when embeddings are present. The vector index/table is dimension-locked; mixing incompatible embedding dimensions in one store is rejected rather than silently corrupting retrieval behavior.

Postgres is optional infrastructure only. The extraction, conflict-resolution, importance, time-decay, ranking, and public `Memory` semantics remain in the Python SDK instead of being reimplemented in the storage backend.

## Memory Studio

Memory Studio is a deliberately small, local-only, read-only inspection UI that reuses the same `Memory` retrieval path and SQLite store as the SDK. It does not introduce a second backend or persistence layer.

After installing the package, point it at an existing SQLite database:

```bash
memory-studio --db memory.db
```

Then open `http://127.0.0.1:8765`. Studio discovers user scopes present in the local database, lets you switch between them, search the selected user's memories, filter by memory kind, see visible/total counts, and open a focused detail page for an individual memory. Kind options include per-kind counts for the current retrieved scope. Detail navigation preserves the active search and kind filter.

You can still choose the initial scope explicitly when useful:

```bash
memory-studio --db memory.db --user-id user-123
```

The default bind address is loopback-only. Studio remains read-only and shows memory kind, key, value, importance, embedding presence, and created/updated timestamps. The `--limit` option controls the maximum number of retrieved memories shown for the selected user.

## n8n community node

Phase 3 lives in `n8n/` as `n8n-nodes-ai-memory-sdk`. The node keeps the architecture local-first by invoking the installed Python SDK through the `memory-sdk-bridge` executable instead of duplicating storage and ranking logic in TypeScript. It exposes Save, Retrieve, Search, and Forget operations for self-hosted n8n.

The Python SDK and n8n must share access to the configured SQLite path. Text Save uses LiteLLM extraction, Search uses local FastEmbed embeddings, and Forget is scoped by both user ID and memory ID.

## TypeScript client

The optional TypeScript package lives in `typescript/` as `ai-memory-sdk-client`. It is intentionally a thin typed client: the Python SDK remains the source of truth for extraction, conflict resolution, scoring, ranking, embeddings, and persistence.

Install the Python SDK first so the local `memory-sdk-bridge` executable is available, then install/build the TypeScript client:

```bash
pip install ai-memory-sdk
cd typescript
npm install
npm run build
```

Create a process-backed client and point it at the same local SQLite database used by Python:

```ts
import { MemoryClient, ProcessBridgeTransport } from 'ai-memory-sdk-client';

const memory = new MemoryClient(
  new ProcessBridgeTransport({
    databasePath: './memory.db',
  }),
);

await memory.save({
  userId: 'user-123',
  key: 'favorite_language',
  value: 'Python',
});

const memories = await memory.retrieve('user-123', { limit: 20 });
const matches = await memory.search({
  userId: 'user-123',
  query: 'programming language',
  limit: 5,
});

if (matches[0]) {
  await memory.forget({
    userId: 'user-123',
    memoryId: matches[0].id,
  });
}
```

`ProcessBridgeTransport` defaults to `memory-sdk-bridge` and `./memory.db`; `bridgeCommand`, `databasePath`, and `llmModel` can be overridden when needed. Transport delegation is the architectural boundary: the TypeScript package does not implement a second memory engine.

## Roadmap

The defined Phase 0–4 roadmap is complete:

- Phase 0: core save/retrieve pipeline.
- Phase 1: conflict resolution, importance scoring, and time decay.
- Phase 2: Memory Studio.
- Phase 3: n8n community node package.
- Phase 4: optional Postgres + pgvector and thin TypeScript SDK.
