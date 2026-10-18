import assert from 'node:assert/strict';
import test from 'node:test';
import { BridgeError } from '../src/errors.js';
import { ProcessBridgeTransport } from '../src/processTransport.js';

const request = { operation: 'retrieve', userId: 'alice' } as const;
function transport(script: string, options = {}) {
  return new ProcessBridgeTransport({
    bridgeCommand: process.execPath, bridgeArgs: ['-e', script, '--'], ...options,
  });
}

for (const [script, code, options] of [
  ['setInterval(() => {}, 1000)', 'TIMEOUT', { timeoutMs: 100 }],
  ["process.stdout.write('x'.repeat(10000))", 'OUTPUT_LIMIT', { maxBufferBytes: 100 }],
  ['process.exit(2)', 'PROCESS', {}],
  ["console.log('not-json')", 'PROTOCOL', {}],
  ["console.log('[]')", 'PROTOCOL', {}],
  ['', 'PROTOCOL', {}],
] as const) {
  test(`transport reports ${code} for ${script}`, async () => {
    await assert.rejects(transport(script, options).execute(request),
      (error: unknown) => error instanceof BridgeError && error.code === code);
  });
}

test('missing executable produces a typed process error', async () => {
  await assert.rejects(new ProcessBridgeTransport({ bridgeCommand: 'missing-memory-sdk-binary' })
    .execute(request), (error: unknown) => error instanceof BridgeError && error.code === 'PROCESS');
});

test('transport rejects unbounded or invalid process limits', () => {
  for (const value of [0, -1, NaN, Infinity, 1.5]) {
    assert.throws(() => new ProcessBridgeTransport({ timeoutMs: value }), RangeError);
    assert.throws(() => new ProcessBridgeTransport({ maxBufferBytes: value }), RangeError);
  }
});
