# n8n AI Memory SDK node

Self-hosted n8n community node for the local-first AI Memory SDK.

## Operations

- **Save** — save unstructured text through the SDK extraction pipeline or persist a structured memory.
- **Retrieve** — return ranked memories for one user.
- **Search** — semantic search using the SDK's local FastEmbed/ONNX embedding path and sqlite-vec when available.
- **Forget** — delete one memory, scoped to the supplied user ID.

## Local runtime contract

This package deliberately does not implement a second memory backend in TypeScript. It invokes the installed Python SDK through `memory-sdk-bridge` using stdin/stdout JSON and `shell: false`.

Install the Python project in the same self-hosted environment as n8n so `memory-sdk-bridge` is on `PATH`, or set **Bridge Command** to its absolute path. The n8n process must also be able to access the configured SQLite **Database Path**.

Text Save requires a LiteLLM model identifier plus whatever provider credentials that model normally uses. Structured Save, Retrieve, and Forget do not require an LLM. Search uses the local FastEmbed adapter.

This integration is intended for self-hosted/local n8n deployments. It does not add a hosted memory service.
