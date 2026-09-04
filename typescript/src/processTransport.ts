import { spawnSync } from 'node:child_process';

import type { MemoryTransport } from './transport.js';
import type { BridgeRequest, BridgeResponse } from './types.js';

export interface ProcessBridgeTransportOptions {
  bridgeCommand?: string;
  databasePath?: string;
  llmModel?: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export class ProcessBridgeTransport implements MemoryTransport {
  private readonly bridgeCommand: string;
  private readonly databasePath: string;
  private readonly llmModel?: string;

  constructor(options: ProcessBridgeTransportOptions = {}) {
    this.bridgeCommand = options.bridgeCommand ?? 'memory-sdk-bridge';
    this.databasePath = options.databasePath ?? './memory.db';
    this.llmModel = options.llmModel?.trim() || undefined;
  }

  async execute(request: BridgeRequest): Promise<BridgeResponse> {
    const args = ['--db', this.databasePath];
    if (this.llmModel) {
      args.push('--llm-model', this.llmModel);
    }

    const result = spawnSync(this.bridgeCommand, args, {
      input: JSON.stringify(request),
      encoding: 'utf8',
      shell: false,
    });

    if (result.error) {
      throw result.error;
    }
    if (result.status !== 0) {
      const stderr = result.stderr.trim();
      throw new Error(stderr || `memory-sdk bridge exited with status ${result.status}`);
    }

    const stdout = result.stdout.trim();
    if (!stdout) {
      throw new Error('memory-sdk bridge returned an empty response');
    }

    let parsed: unknown;
    try {
      parsed = JSON.parse(stdout);
    } catch (error) {
      throw new Error('memory-sdk bridge returned invalid JSON', { cause: error });
    }

    if (!isRecord(parsed)) {
      throw new Error('memory-sdk bridge returned an invalid response object');
    }
    return parsed as unknown as BridgeResponse;
  }
}
