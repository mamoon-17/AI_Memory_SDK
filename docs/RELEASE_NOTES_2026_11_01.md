# SDK reliability update — November 1, 2026

## Storage integrity

- SQLite updates preserve row IDs, preventing duplicate/orphan index rows on repeated writes.
- Both built-in stores invalidate vectors when embeddings are cleared or changed to an
  incompatible dimension. Stored facts remain available through fallback ranking.
- Regression tests inspect real SQLite vector tables; PostgreSQL cases run against pgvector in CI.

## Input and response contracts

- Positive integer limits are required in Python and the JSON bridge. Numeric strings,
  booleans, fractions and null are rejected before storage or provider work.
- SDK scopes and forget IDs must be nonblank strings. Invalid user scopes never reach
  extraction or retrieval providers.
- The TypeScript client validates every returned memory record and reports malformed
  fields/envelopes as `BridgeError` with code `PROTOCOL`. Valid extra fields are preserved.
  Custom transports must provide the complete `MemoryFact` contract, including a null
  or nonempty numeric embedding and timezone-qualified timestamps.

See [input contracts](INPUT_CONTRACTS.md) for compatibility notes and transaction limits.

## Validation

Local checks: 84 Python tests passed, 3 PostgreSQL integration cases skipped without a
configured DSN; all 28 TypeScript tests passed including the installed Python bridge;
Ruff passed. CI also runs the three PostgreSQL cases and the n8n runtime smoke test.
These checks do not claim atomicity across fact/vector transactions or repair of old
index corruption. Existing database backups remain advisable before maintenance.

## Commit provenance

This batch contains exactly 15 development commits: 12 with author/committer dates on
October 31, 2026 and 3 on November 1, 2026, in Asia/Karachi (+05:00). October 31 dates
were assigned retrospectively at the maintainer's request; actual work was performed
November 1. GitHub PR creation, CI and merge timestamps retain their actual service dates.
