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
- Phase 3: user-scoped `Memory.forget()`, local stdin/stdout `memory-sdk-bridge`, and n8n community node package exposing Save / Retrieve / Search / Forget.
- Phase 3 scaffold fixed for installed n8n-workflow connection typing and validated green in Python and n8n CI on `82b8a61e82720e6a9c8151c829caf075a8de78f1`.
- Phase 3 process-level bridge tests and npm package validation in `6048d91a884852e5cbcc600878be3ef638143778` validated green in GitHub Actions.
- Phase 3 self-hosted runtime validation completed on CI run 41 for `96190312ee29cd266565eee6372c1be41fc7a02a`: the exact packed `.tgz` loaded in n8n 2.36.8 on Node 24 and n8n's generated node catalog contained both `aiMemory` and `AI Memory SDK`.
- Phase 3 complete.
- Phase 4 Postgres + pgvector Standard-tier slice: backend-neutral `MemoryStore` protocol, optional store injection into `Memory`, `PostgresMemoryStore`, opt-in `postgres` dependency extra, dimension-locked pgvector KNN, and fallback-compatible embedding persistence.
- Phase 4 Postgres integration validated green on CI run 44 for `943f0aa9a3d6cdd830440f197d384c6f4da4df6e`, including Ruff, Python tests against a real `pgvector/pgvector:pg16` service, n8n build/package validation, and self-hosted n8n runtime smoke.
- Postgres setup and `Memory(store=...)` usage documented in `README.md`.
- Phase 4 thin TypeScript client: typed `MemoryClient`, `MemoryTransport` abstraction, `ProcessBridgeTransport`, Save / Retrieve / Search / Forget delegation, unit tests, Python-bridge integration test, npm package validation, and dedicated CI job.
- TypeScript slice validated green on CI run 48 for `5afb458c36a2a43ba592e43a431f0310925edb96`: Python lint/tests, n8n build/package validation, TypeScript typecheck/tests/bridge integration/package validation, and self-hosted n8n runtime smoke all passed.
- TypeScript usage documented in the root `README.md` in `e184e7be6db701879cea000a0fd4fc0c06ac415a`.
- Phase 4 complete.
- Defined Phase 0–4 roadmap complete.

## Current milestone

No active roadmap milestone. The defined Phase 0–4 scope is complete. Do not broaden scope without a new explicit product decision or roadmap item.

## Validation status

CI runs 49 and 50 for the documentation-only closure commits failed only in `n8n-runtime-smoke` while installing the pinned `n8n@2.36.8` runtime. Python tests/lint, n8n typecheck/build/package validation, and TypeScript typecheck/tests/bridge integration/package validation all remained green. The runtime install failed before n8n started because npm 11 attempted to resolve optional peer dependencies to an unpublished `@tiptap/extensions@3.31.3` version. This is dependency-resolution churn inside the pinned n8n dependency graph, not a product-code regression.

Commit `cbfe37897ae7bea01814b5c8b95acdd5f4c1e756` updates only the pinned n8n runtime install to use `npm install --legacy-peer-deps`, preserving n8n 2.36.8 and the same runtime registration acceptance check while avoiding unrelated optional-peer resolution. Replacement CI must be green before the repository is declared fully healthy.

## Next action

Inspect CI for `cbfe37897ae7bea01814b5c8b95acdd5f4c1e756` first. If all four jobs pass, the defined Phase 0–4 roadmap is complete and no further implementation is required. Stop rather than inventing Phase 5 work. If `n8n-runtime-smoke` is still red, inspect the install/runtime logs and fix the reproducible blocker before doing anything else.

## Architectural guardrails

- Python SDK first.
- SQLite + sqlite-vec remains the default local storage profile.
- Postgres + pgvector is optional Standard-tier infrastructure only.
- Local FastEmbed/ONNX embeddings.
- LiteLLM for provider-agnostic extraction.
- LangGraph in-process orchestration.
- Memory Studio remains local and read-only.
- n8n integration calls the local Python SDK through a narrow bridge rather than reimplementing memory semantics.
- TypeScript SDK remains thin and delegates to Python rather than duplicating memory semantics.
- No hosted SaaS, Kubernetes, Neo4j, Redis, or Celery in the default profile.
