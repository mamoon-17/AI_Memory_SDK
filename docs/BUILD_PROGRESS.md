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
- Unit coverage for user isolation, ranking, invalid limits, pipeline deduplication, blank input, conflict replacement, importance policy, time decay, vector ranking, sqlite-vec user scoping, and delayed-extension backfill.
- GitHub Actions lint/test workflow.
- CI lint regression from the provider/pipeline slice fixed.
- Phase 1 quality-policy head validated green in GitHub Actions after fixing import-order lint.
- Phase 2 first slice: local read-only Memory Studio with user-scoped list/search, metadata inspection, HTML escaping, loopback-only default binding, CLI entry point, tests, and README usage docs.

## Current milestone

Phase 2 — Memory Studio.

## Validation status

Phase 1 is complete and green in GitHub Actions. The first Memory Studio slice has been pushed and its GitHub Actions validation is pending/in progress.

## Next action

First inspect the latest Memory Studio CI result and fix any lint/test/install regression before new work. If green, continue Phase 2 with user discovery/filtering and a focused memory-detail view while keeping Studio read-only and reusing the SDK/storage path.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only until the inspection experience is solid.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
