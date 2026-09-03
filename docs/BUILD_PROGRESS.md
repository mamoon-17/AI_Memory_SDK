# Build Progress

## Completed

- Repository/package foundation.
- Structured `MemoryFact` model and local SQLite fact store.
- Public `Memory` client with user-scoped structured `save()` and `retrieve()` APIs.
- Provider-neutral extraction and embedding protocols.
- Lazy LiteLLM fact extraction and local FastEmbed/ONNX embedding adapters.
- LangGraph in-process Phase 0 save pipeline: classify → extract → exact dedup → embed → store.
- Embedding persistence in SQLite.
- sqlite-vec default dependency, lazy extension loading, dimension-aware vector table migration/backfill, and user-scoped database-side KNN retrieval.
- Safe in-process cosine and lexical fallbacks when sqlite-vec cannot load or cannot serve the configured dimension.
- Unit coverage for user isolation, ranking, invalid limits, pipeline deduplication, blank input, vector ranking, sqlite-vec user scoping, and delayed-extension backfill.
- GitHub Actions lint/test workflow.
- CI lint regression from the provider/pipeline slice fixed; install, Ruff, and pytest returned green before vector-store work began.

## Current milestone

Phase 0 — core memory pipeline and default local vector storage.

## Validation status

The pre-vector-store head is green in GitHub Actions. The sqlite-vec slice is designed to exercise the real extension in CI while also testing the fallback/backfill path. The new head must pass Ruff and pytest before Phase 0 is considered stable.

## Next action

Validate the sqlite-vec slice in GitHub Actions. If green, Phase 0 is stable enough to begin Phase 1 with conflict resolution first, then importance scoring and time decay. Preserve user scoping and deterministic provider-free tests while adding those policies to the LangGraph pipeline.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
