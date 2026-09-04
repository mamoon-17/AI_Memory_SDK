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

Python tests and the regular n8n typecheck/build/package jobs remain green. The latest main CI showed n8n 2.36.8 starting successfully on Node 24, finishing migrations, and exposing the editor, but the node catalog never contained AI Memory SDK. The root cause is no longer startup timing: a raw `npm install` under the n8n user `nodes` directory is not equivalent to n8n's managed community-package installation because modern n8n tracks installed community packages in its database. Commit `306cbcb1a7b6af7536b247d4204a3259840cfd55` keeps building and installing the exact packed `.tgz`, verifies the packaged node JS/SVG exist, and then points `N8N_CUSTOM_EXTENSIONS` at that packed artifact's compiled node directory. This tests whether the actual publishable artifact can be discovered and registered by a real self-hosted n8n runtime without fabricating n8n package database rows. The public `/types/nodes.json` assertion still requires both `aiMemory` and `AI Memory SDK`.

## Next action

Inspect CI for `306cbcb1a7b6af7536b247d4204a3259840cfd55` (and the checkpoint commit after it). If the runtime smoke is green, record Phase 3 runtime compatibility as validated and assess Phase 3 complete; actual installation through n8n's managed Community Nodes UI remains a publication/registry concern, not something CI should simulate by mutating internal database tables. If the packed artifact still fails to register through `N8N_CUSTOM_EXTENSIONS`, inspect the node loader error and package metadata/path before any Phase 4 work. Do not weaken the exact node-catalog assertion, fake `installed_packages` database state, add a hosted service, or duplicate SDK storage logic in TypeScript.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- n8n integration calls the local Python SDK through a narrow bridge rather than reimplementing memory semantics.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
