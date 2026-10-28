import assert from 'node:assert/strict';
import test from 'node:test';
import { ProcessBridgeTransport } from '../src/processTransport.js';

export function scripted(script: string, options = {}) {
  return new ProcessBridgeTransport({
    bridgeCommand: process.execPath, bridgeArgs: ['-e', script, '--'], ...options,
  });
}

test('transport is nonblocking while the child is running', async () => {
  const transport = scripted(`process.stdin.resume(); process.stdin.on('end', () => {
    setTimeout(() => console.log('{"memories":[]}'), 250);
  });`);
  let settled = false;
  const pending = transport.execute({ operation: 'retrieve', userId: 'alice' })
    .then(result => { settled = true; return result; });
  await new Promise(resolve => setTimeout(resolve, 10));
  assert.equal(settled, false);
  assert.deepEqual(await pending, { memories: [] });
});

test('transport passes Unicode request through stdin', async () => {
  const transport = scripted(`let data=''; process.stdin.on('data', c => data+=c);
    process.stdin.on('end', () => console.log(JSON.stringify({memories:[JSON.parse(data)]})));`);
  const result = await transport.execute({ operation: 'save', userId: 'alice', key: 'café', value: '茶' });
  assert.ok('memories' in result);
  assert.equal(result.memories[0]?.value, '茶');
});
