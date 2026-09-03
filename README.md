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

## Roadmap

- Phase 0: core save/retrieve pipeline.
- Phase 1: conflict resolution, importance scoring, and time decay.
- Phase 2: Memory Studio.
- Phase 3: n8n community node package.
- Phase 4: optional Postgres + pgvector and TypeScript SDK.
