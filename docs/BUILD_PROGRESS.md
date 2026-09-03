# Build Progress

## Completed

- Repository/package foundation.
- Structured `MemoryFact` model and local SQLite fact store.
- Public `Memory` client with user-scoped structured `save()` and `retrieve()` APIs.
- Provider-neutral extraction and embedding protocols.
- Lazy LiteLLM fact extraction and local FastEmbed/ONNX embedding adapters.
- LangGraph in-process pipeline: classify → extract → exact dedup → conflict resolution → embed → store.
- Deterministic Phase 1 conflict policy: for the same user + kind + key, a newly extracted different value supersedes the prior value; exact duplicates remain no-ops and other users are isolated.
- Embedding persistence in SQLite.
- sqlite-vec default dependency, lazy extension loading, dimension-aware vector table migration/backfill, and user-scoped database-side KNN retrieval.
- Safe in-process cosine and lexical fallbacks when sqlite-vec cannot load or cannot serve the configured dimension.
- Unit coverage for user isolation, ranking, invalid limits, pipeline deduplication, blank input, conflict replacement, vector ranking, sqlite-vec user scoping, and delayed-extension backfill.
- GitHub Actions lint/test workflow.
- CI lint regression from the provider/pipeline slice fixed.
- sqlite-vec slice validated green in GitHub Actions: install, Ruff, and pytest all passed.

## Current milestone

Phase 1 — memory quality policies.

## Validation status

The sqlite-vec Phase 0 head is green in GitHub Actions. Conflict resolution is implemented as a deterministic, provider-free graph node and must be validated on the new head before continuing Phase 1.

## Next action

Validate conflict resolution in GitHub Actions. If green, add a deterministic importance-scoring policy that combines extractor confidence with memory-type/value heuristics without requiring another model call, then incorporate time decay into retrieval scoring. Keep conflict replacement user-scoped and preserve sqlite-vec/cosine fallback behavior.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
