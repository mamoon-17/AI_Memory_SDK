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
- First Memory Studio slice validated green in GitHub Actions.
- Phase 2 second slice: local user discovery/filtering, optional initial user scope, user-scoped memory detail pages, safe navigation/query preservation, and storage tests preventing cross-user detail access.

## Current milestone

Phase 2 — Memory Studio.

## Validation status

Phase 1 is complete and green in GitHub Actions. The first Memory Studio slice is green. The second Studio slice is implemented and awaiting CI validation.

## Next action

Inspect CI for the user-discovery/detail slice first. If green, finish the small Phase 2 inspection experience with summary counts/filter polish and documentation, then decide whether Memory Studio is sufficient to mark Phase 2 complete before starting the n8n community node package.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only until the inspection experience is solid.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
