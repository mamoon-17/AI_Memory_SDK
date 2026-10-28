# Developer needs and implementation decisions

Research performed October 28, 2026. This document extends the original design;
the repository remains a local-first memory engine. Commit author/committer dates
were assigned retrospectively at the maintainer's request and do not date this research.

## Evidence and limitations

Community threads are qualitative signals, not a representative developer survey.
Some replies promote their own products. We use reported problems to choose tests
and features, not to endorse performance claims or competitors' marketing.

- [Local memory that still needs remote API keys](https://www.reddit.com/r/LLMDevs/comments/1rdv0jz/saw_openmemory_by_mem0_it_boasts_locally_running/)
  raises a privacy expectation: document precisely which operations invoke providers.
- [Memory makes debugging harder](https://www.reddit.com/r/LLMDevs/comments/1s72x58/memory_made_my_agent_harder_to_debug_not_easier/)
  motivates inspectable records, explicit filters, and portable scoped exports.
- [Temporal reasoning and privacy controls](https://www.reddit.com/r/LocalLLaMA/comments/1ra0ude/ai_memory_layers_are_promising_but_3_things_still/)
  motivates time filters and explicit deletion. Full historical versioning remains future work.
- [Asyncio force timeout](https://stackoverflow.com/questions/28609534/python-asyncio-force-timeout)
  illustrates the user-facing problem of blocking work inside an async API.
- [Subprocess timeout](https://stackoverflow.com/questions/10756383/timeout-on-subprocess-readline-in-python)
  highlights bounded waiting and safe subprocess lifecycle handling.
- [Mem0 local export discussion](https://github.com/mem0ai/mem0/discussions/5967)
  is additional first-party evidence for portable, user-scoped data access.

## Implementation priorities

1. Validated records and exact kind/key/importance/time filtering before ranking.
2. Complete scoped listing plus versioned JSON export/import with ownership checks.
3. Async Python entry points that offload synchronous work; explicit cancellation limits.
4. Scoped bulk deletion with a count and no global default.
5. Nonblocking TypeScript subprocess transport, timeouts, bounded output, typed failures.
6. Offline lexical bridge search and filters without silently downloading a model.

## Technical basis

[Python asyncio.to_thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread)
supports offloading blocking I/O; cancelling the await does not stop a worker thread.
[Node child_process](https://nodejs.org/api/child_process.html) distinguishes blocking
sync calls from asynchronous execFile/spawn and documents timeout/maxBuffer options.
[SQLite connection contexts](https://docs.python.org/3/library/sqlite3.html#how-to-use-the-connection-context-manager)
commit/rollback but do not close connections, which matters for long-running clients.

## Deliberate limits

No benchmark wins are claimed. Metadata schemas, TTL sweeps, hybrid scored explanations,
MCP servers, encryption key management, historical versioning, and automatic retries
need separate design. Retrying a mutating operation without an idempotency contract can
duplicate memories. Filtering and portable exports favor correctness over large-scale
performance: they currently load the user's records before processing.
