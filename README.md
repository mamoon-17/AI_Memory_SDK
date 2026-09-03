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

## Roadmap

- Phase 0: core save/retrieve pipeline.
- Phase 1: conflict resolution, importance scoring, and time decay.
- Phase 2: Memory Studio.
- Phase 3: n8n community node package.
- Phase 4: optional Postgres + pgvector and TypeScript SDK.
