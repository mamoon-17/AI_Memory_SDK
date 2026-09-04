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

Python tests and the regular n8n typecheck/build/package jobs remain green. CI run 38 reached a healthy n8n 2.36.8 editor on Node 24 and confirmed the exact packed `.tgz` installed with its compiled node JS/SVG present, but the node catalog still did not contain AI Memory SDK. The failure is isolated to custom-extension discovery. The previous workflow pointed `N8N_CUSTOM_EXTENSIONS` at the deepest compiled `dist/nodes/AiMemory` directory. n8n's custom-node contract is to point that variable at the custom extensions root where packages are installed so the loader can discover package contents below it. Commit `e0e779fee7026d54cdd696ef086dfff0f3a7c1a9` corrects the runtime smoke to use `$RUNNER_TEMP/n8n-user/nodes` as that root while preserving the packed-artifact installation and the exact `aiMemory` + `AI Memory SDK` catalog assertion.

## Next action

Inspect CI for `e0e779fee7026d54cdd696ef086dfff0f3a7c1a9`. If the self-hosted runtime smoke is green and `/types/nodes.json` contains both `aiMemory` and `AI Memory SDK`, record Phase 3 runtime compatibility as validated and assess Phase 3 complete before starting optional Phase 4. If registration still fails, inspect n8n loader output and the package metadata/layout under the custom extensions root before changing timeouts or attempting managed-package database simulation. Do not weaken the exact node-catalog assertion, fake `installed_packages` database state, add a hosted service, or duplicate SDK storage logic in TypeScript.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- n8n integration calls the local Python SDK through a narrow bridge rather than reimplementing memory semantics.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
