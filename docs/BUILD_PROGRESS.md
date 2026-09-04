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

Python tests and the regular n8n typecheck/build/package jobs remain green. CI run 40 on `944c9b7aebba06207630bd7083cd0f9b12bee094` confirmed the exact packed `.tgz` installs with its compiled node JS/SVG present and n8n 2.36.8 reaches a healthy editor on Node 24, but the runtime smoke still failed its catalog assertion. Inspection of the pinned n8n 2.36.8 source showed the smoke's oracle was wrong: `/types/nodes.json` is protected by editor authentication and is served from n8n's generated static cache, so unauthenticated `curl --fail` cannot prove whether the custom node registered. The current CI fix keeps the packed-artifact install and `N8N_CUSTOM_EXTENSIONS` loader path unchanged, but validates the generated `$N8N_USER_FOLDER/.cache/n8n/public/types/nodes.json` file directly and still requires both `aiMemory` and `AI Memory SDK`.

## Next action

Inspect CI for the generated-catalog smoke fix. If the self-hosted runtime smoke is green and the generated node catalog contains both `aiMemory` and `AI Memory SDK`, record Phase 3 runtime compatibility as validated and assess Phase 3 complete before starting optional Phase 4. If registration still fails, use the added static-cache listing and loader-related runtime log diagnostics to identify an actual module/discovery error before changing package metadata or loader paths. Do not weaken the exact node-catalog assertion, fake `installed_packages` database state, add a hosted service, or duplicate SDK storage logic in TypeScript.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec default local storage.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- n8n integration calls the local Python SDK through a narrow bridge rather than reimplementing memory semantics.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
