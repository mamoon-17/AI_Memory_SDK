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
- n8n distribution will expose Save, Retrieve, Search, and Forget nodes.

## Local vector search

The default Python install includes `sqlite-vec`. The SDK loads the extension only when an embedding needs to be indexed or searched, creates the vector table lazily using the embedding dimension, and performs user-scoped KNN queries inside SQLite.

If the host Python/SQLite build cannot load extensions, facts and embeddings are still persisted normally. Retrieval safely falls back to in-process cosine ranking and then lexical ranking instead of making the local SDK unusable. Python builds with loadable SQLite extensions are therefore recommended for the default accelerated path.

## Memory Studio

Memory Studio is a deliberately small, local-only, read-only inspection UI that reuses the same `Memory` retrieval path as the SDK. It does not introduce a second backend or persistence layer.

After installing the package, point it at an existing SQLite database and a user scope:

```bash
memory-studio --db memory.db --user-id user-123
```

Then open `http://127.0.0.1:8765`. The first slice supports listing and searching memories and inspecting kind, key, value, importance, and created/updated timestamps. The default bind address is loopback-only.

## Roadmap

- Phase 0: core save/retrieve pipeline.
- Phase 1: conflict resolution, importance scoring, and time decay.
- Phase 2: Memory Studio.
- Phase 3: n8n community node package.
- Phase 4: optional Postgres + pgvector and TypeScript SDK.
