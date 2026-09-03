# Build Progress

## Completed

- Repository/package foundation.
- Structured `MemoryFact` model and local SQLite fact store.
- Public `Memory` client with user-scoped structured `save()` and `retrieve()` APIs.
- Provider-neutral extraction and embedding protocols.
- Lazy LiteLLM fact extraction and local FastEmbed/ONNX embedding adapters.
- LangGraph in-process Phase 0 save pipeline: classify → extract → exact dedup → embed → store.
- Embedding persistence in SQLite plus vector similarity retrieval when an embedder is configured.
- Deterministic lexical retrieval remains as a dependency/provider fallback.
- Unit coverage for user isolation, ranking, invalid limits, pipeline deduplication, blank input, and vector ranking.
- GitHub Actions lint/test workflow exists.

## Current milestone

Phase 0 — core memory pipeline.

## Validation status

The provider/pipeline slice has deterministic provider-free tests using fakes. The repository CI is configured to install the package and run Ruff + pytest. CI status should be checked on the new head before this slice is considered fully green.

## Next action

Finish Phase 0 vector storage by integrating sqlite-vec for database-side nearest-neighbor search, while retaining a safe Python cosine fallback when the extension cannot load. Add migrations/tests for sqlite-vec availability and document the default local installation path. Do not begin Phase 1 conflict resolution until the vector store path is stable.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
