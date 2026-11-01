# Identifier and limit contracts

Python user IDs and memory IDs must be nonblank strings. Python preserves valid
identifiers exactly, including surrounding spaces; the JSON bridge continues to trim
user IDs for compatibility with its existing workflow behavior. Use one normalized
identifier convention in applications that combine the two entry points.

Invalid scopes are rejected before retrieval embeddings or extraction providers run.
The async Python facade delegates to these same checks on its worker.

Retrieval limits in Python and bridge JSON must be positive integers. Booleans,
fractional numbers, numeric strings, and null are rejected instead of being truncated
or coerced. Omit the bridge field to use its default of 10. This is a tightening of
runtime validation: callers that sent string limits must send JSON numbers instead.

# Updating stored embeddings

SQLite upserts now preserve a fact's row identity, avoiding orphaned vector rows
on repeated writes. Clearing an embedding or replacing it with an incompatible
dimension invalidates the previous index entry in both built-in stores. Original
fact data stays persisted even if vector acceleration is unavailable; fallback
ranking remains available. An incompatible vector does not change the existing
store's configured embedding dimension.

Fact and vector writes still use separate transactions. These changes do not provide
atomic updates across those transactions or repair pre-existing orphaned index rows.
If the SQLite extension cannot be loaded during an update, the SDK cannot modify
that index; coordinate maintenance before relying on accelerated retrieval again.
