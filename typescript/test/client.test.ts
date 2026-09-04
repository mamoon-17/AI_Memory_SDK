import assert from 'node:assert/strict';
import test from 'node:test';

import { MemoryClient } from '../src/client.js';
import type { MemoryTransport } from '../src/transport.js';
import type { BridgeRequest, BridgeResponse, MemoryFact } from '../src/types.js';

const fact: MemoryFact = {
  id: 'memory-1',
  user_id: 'user-1',
  kind: 'preference',
  key: 'language',
  value: 'Python',
  importance: 0.8,
  embedding: null,
  created_at: '2026-09-04T00:00:00Z',
  updated_at: '2026-09-04T00:00:00Z',
};

class RecordingTransport implements MemoryTransport {
  readonly requests: BridgeRequest[] = [];

  constructor(private readonly responses: BridgeResponse[]) {}

  async execute(request: BridgeRequest): Promise<BridgeResponse> {
    this.requests.push(request);
    const response = this.responses.shift();
    if (!response) {
      throw new Error('missing test response');
    }
    return response;
  }
}

test('save delegates text and structured requests to the transport', async () => {
  const transport = new RecordingTransport([{ memories: [fact] }, { memories: [fact] }]);
  const client = new MemoryClient(transport);

  assert.deepEqual(await client.save({ userId: 'user-1', text: 'I prefer Python' }), [fact]);
  assert.deepEqual(
    await client.save({
      userId: 'user-1',
      key: 'language',
      value: 'Python',
      kind: 'preference',
      importance: 0.8,
    }),
    [fact],
  );

  assert.deepEqual(transport.requests, [
    { operation: 'save', userId: 'user-1', text: 'I prefer Python' },
    {
      operation: 'save',
      userId: 'user-1',
      key: 'language',
      value: 'Python',
      kind: 'preference',
      importance: 0.8,
    },
  ]);
});

test('retrieve, search, and forget preserve the Python bridge protocol', async () => {
  const transport = new RecordingTransport([
    { memories: [fact] },
    { memories: [fact] },
    { forgotten: true },
  ]);
  const client = new MemoryClient(transport);

  assert.deepEqual(await client.retrieve('user-1', { limit: 4 }), [fact]);
  assert.deepEqual(await client.search({ userId: 'user-1', query: 'language', limit: 2 }), [fact]);
  assert.equal(await client.forget({ userId: 'user-1', memoryId: 'memory-1' }), true);

  assert.deepEqual(transport.requests, [
    { operation: 'retrieve', userId: 'user-1', limit: 4 },
    { operation: 'search', userId: 'user-1', query: 'language', limit: 2 },
    { operation: 'forget', userId: 'user-1', memoryId: 'memory-1' },
  ]);
});

test('client rejects mismatched bridge response shapes', async () => {
  const transport = new RecordingTransport([{ forgotten: false }]);
  const client = new MemoryClient(transport);

  await assert.rejects(() => client.retrieve('user-1'), /without memories/);
});
