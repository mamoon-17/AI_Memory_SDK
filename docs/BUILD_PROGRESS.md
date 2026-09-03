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
- Phase 0 and Phase 1 validated green in GitHub Actions.
- Phase 2 Memory Studio: local read-only UI with user discovery/switching, search, memory-kind filtering with counts, visible/total summary counts, user-scoped memory detail pages, preserved filter navigation, HTML escaping, loopback-only default binding, CLI entry point, tests, and README usage docs.
- Memory Studio user discovery/detail slice validated green in GitHub Actions.
- Final Memory Studio inspection polish implemented in `bae7e1d20ebb977d962a8dc143d737bd40e47630`.

## Current milestone

Phase 2 — Memory Studio final validation.

## Validation status

Latest `main` was green before the final Memory Studio filter/count polish. The final Phase 2 slice must pass GitHub Actions before Phase 2 is marked complete.

## Next action

Inspect CI for the final Memory Studio filter/count polish. If green, mark Phase 2 complete and start Phase 3 with the minimal n8n community node package scaffold and the Save / Retrieve / Search / Forget operation contract. Do not add a hosted service; keep the integration local-first.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
