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
- Phase 3 first slice: user-scoped `Memory.forget()`, local stdin/stdout `memory-sdk-bridge`, and n8n community node package exposing Save / Retrieve / Search / Forget.
- Phase 3 scaffold fixed for installed n8n-workflow connection typing and validated green in Python and n8n CI on `82b8a61e82720e6a9c8151c829caf075a8de78f1`.
- Phase 3 process-level bridge tests and npm package validation in `6048d91a884852e5cbcc600878be3ef638143778` validated green in GitHub Actions.

## Current milestone

Phase 3 — n8n community node package.

## Validation status

Python tests and the regular n8n typecheck/build/package jobs are green. The Node 24 runtime fix succeeded: self-hosted n8n 2.36.8 now installs and starts successfully. CI run 26 still failed only in the registration assertion because the smoke test queried `/rest/node-types`, whose first-run response was not JSON and caused `JSONDecodeError`. The assertion was corrected in `1e762efd294aba13452aa575489c086a52b0abb8` to query n8n's public `/types/nodes.json` catalog instead, which is the endpoint used to expose the node catalog without requiring editor-session setup.

## Next action

Inspect CI for `1e762efd294aba13452aa575489c086a52b0abb8`. If the self-hosted runtime smoke is green and `/types/nodes.json` contains `aiMemory` / `AI Memory SDK`, mark Phase 3 complete and then begin Phase 4 only as optional stretch work. If it fails, inspect the runtime log and continue fixing package loading/registration before any Phase 4 work. Do not weaken the registration assertion, add a hosted service, or duplicate SDK storage logic in TypeScript.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- n8n integration calls the local Python SDK through a narrow bridge rather than reimplementing memory semantics.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
