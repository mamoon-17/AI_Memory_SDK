# Build Progress

## Completed

- Repository/package foundation.
- Structured `MemoryFact` model and local SQLite fact store.
- Public `Memory` client with user-scoped structured `save()` and `retrieve()` APIs.
- Provider-neutral extraction and embedding protocols.
- Lazy LiteLLM fact extraction and local FastEmbed/ONNX embedding adapters.
- LangGraph in-process pipeline: classify → extract → exact dedup → conflict resolution → importance score → embed → store.
- Deterministic Phase 1 conflict policy: for the same user + kind + key, a newly extracted different value supersedes the prior value; exact duplicates remain no-ops and other users are isolated.
- Deterministic importance scoring combining extractor signal with memory-kind and value-specificity heuristics without another model call.
- Retrieval quality ranking combines semantic/lexical relevance with stored importance and exponential time decay; no-query retrieval balances importance and recency.
- Embedding persistence in SQLite.
- sqlite-vec default dependency, lazy extension loading, dimension-aware vector table migration/backfill, and user-scoped database-side KNN retrieval.
- Safe in-process cosine and lexical fallbacks when sqlite-vec cannot load or cannot serve the configured dimension.
- GitHub Actions lint/test workflow.
- Phase 0 and Phase 1 validated green in GitHub Actions.
- Phase 2 Memory Studio: local read-only UI with user discovery/switching, search, memory-kind filtering with counts, visible/total summary counts, user-scoped memory detail pages, preserved filter navigation, HTML escaping, loopback-only default binding, CLI entry point, tests, and README usage docs.
- Final Memory Studio inspection polish in `bae7e1d20ebb977d962a8dc143d737bd40e47630` validated green in GitHub Actions.
- Phase 2 complete.
- Phase 3: user-scoped `Memory.forget()`, local stdin/stdout `memory-sdk-bridge`, and n8n community node package exposing Save / Retrieve / Search / Forget.
- Phase 3 scaffold fixed for installed n8n-workflow connection typing and validated green in Python and n8n CI on `82b8a61e82720e6a9c8151c829caf075a8de78f1`.
- Phase 3 process-level bridge tests and npm package validation in `6048d91a884852e5cbcc600878be3ef638143778` validated green in GitHub Actions.
- Phase 3 self-hosted runtime validation completed on CI run 41 for `96190312ee29cd266565eee6372c1be41fc7a02a`: the exact packed `.tgz` loaded in n8n 2.36.8 on Node 24 and n8n's generated node catalog contained both `aiMemory` and `AI Memory SDK`.
- Phase 3 complete.
- Phase 4 Postgres + pgvector Standard-tier slice: backend-neutral `MemoryStore` protocol, optional store injection into `Memory`, `PostgresMemoryStore`, opt-in `postgres` dependency extra, dimension-locked pgvector KNN, and fallback-compatible embedding persistence.
- Phase 4 Postgres integration validated green on CI run 44 for `943f0aa9a3d6cdd830440f197d384c6f4da4df6e`, including Ruff, Python tests against a real `pgvector/pgvector:pg16` service, n8n build/package validation, and self-hosted n8n runtime smoke.
- Postgres setup and `Memory(store=...)` usage documented in `README.md`.

## Current milestone

Phase 4 — TypeScript SDK stretch slice. This must remain thin and protocol-facing; Python remains the source of truth for extraction, conflict resolution, scoring, ranking, and storage semantics.

## Validation status

The Postgres + pgvector Standard-tier slice is complete and green. SQLite + sqlite-vec remains the default local storage profile. The README documentation commit follows the already-green implementation and should still be allowed to pass normal CI before any TypeScript work is committed.

## Next action

Inspect CI for the Postgres documentation/checkpoint commits. If red, fix CI before doing anything else. If green, inspect the existing n8n bridge/package and design the smallest useful TypeScript SDK surface that delegates to the Python bridge rather than duplicating the Python pipeline. Favor a typed client exposing Save / Retrieve / Search / Forget semantics with process/transport abstraction and tests. Do not introduce a TypeScript storage engine, extraction pipeline, hosted service, or second source of memory-ranking logic.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec remains the default local storage profile.
- Postgres + pgvector is optional Standard-tier infrastructure only.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- n8n integration calls the local Python SDK through a narrow bridge rather than reimplementing memory semantics.
- TypeScript SDK must remain thin and delegate to Python rather than duplicate memory semantics.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
