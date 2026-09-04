import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';

import { MemoryClient } from '../src/client.js';
import { ProcessBridgeTransport } from '../src/processTransport.js';

const integrationEnabled = process.env.MEMORY_SDK_BRIDGE_INTEGRATION === '1';

test(
  'process transport round-trips structured memory through the installed Python bridge',
  { skip: !integrationEnabled },
  async () => {
    const directory = await mkdtemp(join(tmpdir(), 'memory-sdk-ts-'));
    try {
      const client = new MemoryClient(
        new ProcessBridgeTransport({ databasePath: join(directory, 'memory.db') }),
      );

      const saved = await client.save({
        userId: 'typescript-user',
        key: 'favorite_language',
        value: 'TypeScript',
        kind: 'preference',
        importance: 0.75,
      });
      assert.equal(saved.length, 1);
      assert.equal(saved[0]?.user_id, 'typescript-user');
      assert.equal(saved[0]?.value, 'TypeScript');

      const retrieved = await client.retrieve('typescript-user');
      assert.equal(retrieved.length, 1);
      assert.equal(retrieved[0]?.id, saved[0]?.id);

      assert.equal(
        await client.forget({ userId: 'typescript-user', memoryId: saved[0]!.id }),
        true,
      );
      assert.deepEqual(await client.retrieve('typescript-user'), []);
    } finally {
      await rm(directory, { recursive: true, force: true });
    }
  },
);
