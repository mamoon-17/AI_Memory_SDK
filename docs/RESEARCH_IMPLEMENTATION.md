# Research implementation record

Completed locally on October 28, 2026. Git dates were assigned retrospectively at
the maintainer's request; PR creation, CI and merges retain their real service dates.

## Original design corrections

The original Word design's star counts, funding, prices and benchmark comparisons
are historical assertions, not verified current product facts. They must not be used
as current marketing evidence. Recall@5 and end-to-end task accuracy are different
measurements; comparing their percentages does not establish a quality ranking.

The running code uses a subprocess bridge for n8n/TypeScript, rather than the HTTP
server proposed in the design. Studio is read-only; graph/timeline editing, pinning,
historical versions and publication to package registries are not implemented by
this update. The original phase completion language describes the existing reduced
scope, not every feature proposed in the Word document.

## Delivered changes

- Exact filters before ranking, with aware temporal boundaries.
- Complete scoped listing and versioned, Unicode JSON portability.
- Prevalidated restores with repeated-import handling and collision checks.
- Async Python access with one serial worker and explicit cleanup.
- Scoped filtered bulk forgetting.
- Nonblocking TypeScript bridge with bounded output and execution time.
- Typed process/protocol failures and explicit offline lexical bridge search.
- Deterministic SQLite connection cleanup and reproducible TypeScript installs.

## Local validation

- Python: 58 passed, 1 PostgreSQL integration test skipped without a DSN.
- TypeScript: 15 passed, including installed Python bridge integration.
- Ruff: all checks passed.
- Tests use injected extractors/embedders; no live provider quality benchmark is claimed.
- Full n8n runtime registration and PostgreSQL run in the repository CI workflow.

## Commit schedule

The initial 36 implementation commits use Asia/Karachi (+05:00) timestamps:
6 on October 9, 6 on October 10, 2 per day October 11 through 18,
4 on October 25 and 4 on October 26. Any subsequent validation fixes use October 26.
No existing commits were rewritten. Keep merge commits rather than squashing so
the implementation sequence and assigned dates remain visible.

## Remaining engineering limits

Scope listing, filtering, export and collision checks scan records in memory. JSON
imports and bulk deletion are not atomic across records and require application
coordination during concurrent writes. Cancellation cannot roll back completed
provider or database effects. Deletion does not erase backups. These are documented
API boundaries, not claims of enterprise security or large-scale performance.
