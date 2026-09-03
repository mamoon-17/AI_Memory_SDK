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
- Conflict-resolution head validated green in GitHub Actions.

## Current milestone

Phase 1 — memory quality policies.

## Validation status

The conflict-resolution head is green. Importance scoring and time-decay retrieval are implemented in the current change set and require GitHub Actions validation before Phase 1 is considered complete.

## Next action

Validate the Phase 1 quality-policy slice in GitHub Actions. If green, consider Phase 1 complete and begin Phase 2 Memory Studio with a deliberately small local read-only inspection surface first: list/search memories, inspect metadata/importance/timestamps, and preserve the SDK as the source of truth rather than duplicating storage logic.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
