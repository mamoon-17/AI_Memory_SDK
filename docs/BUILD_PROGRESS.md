# Build Progress

## Completed

- Repository/package foundation.
- Structured `MemoryFact` model and local SQLite fact store.
- Public `Memory` client with user-scoped `save()` and `retrieve()` APIs.
- Deterministic lexical relevance fallback for Phase 0 retrieval.
- Unit coverage for user isolation, ranking, and invalid limits.
- GitHub Actions lint/test workflow exists.

## Current milestone

Phase 0 — core memory pipeline.

## Validation status

The repository has CI configured, but no combined status was available for the previous head when this checkpoint was written. The new client slice is covered by pytest tests and should be validated by the next GitHub Actions run before being treated as fully green.

## Next action

Add pluggable extraction and embedding interfaces, with LiteLLM and local FastEmbed adapters loaded lazily. Then wire a LangGraph in-process save pipeline around classify → extract → dedup → embed → store while keeping tests provider-free through fakes.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
