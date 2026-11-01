import type { MemoryFact } from './types.js';

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function timestamp(value: unknown): value is string {
  return typeof value === 'string' && /(Z|[+-]\d{2}:\d{2})$/i.test(value)
    && Number.isFinite(Date.parse(value));
}

export function isMemoryFact(value: unknown): value is MemoryFact {
  if (!isRecord(value)) return false;
  for (const field of ['id', 'user_id', 'kind', 'key', 'value']) {
    if (typeof value[field] !== 'string' || !value[field].trim()) return false;
  }
  if (typeof value.importance !== 'number' || !Number.isFinite(value.importance)
      || value.importance < 0 || value.importance > 1) return false;
  if (!timestamp(value.created_at) || !timestamp(value.updated_at)) return false;
  return value.embedding === null || (Array.isArray(value.embedding)
    && value.embedding.length > 0
    && value.embedding.every((item: unknown) => typeof item === 'number' && Number.isFinite(item)));
}
