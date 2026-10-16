import { execFile } from 'node:child_process';

import type { MemoryTransport } from './transport.js';
import type { BridgeRequest, BridgeResponse } from './types.js';

export interface ProcessBridgeTransportOptions {
  bridgeCommand?: string;
  databasePath?: string;
  llmModel?: string;
  bridgeArgs?: string[];
  timeoutMs?: number;
  maxBufferBytes?: number;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

export class ProcessBridgeTransport implements MemoryTransport {
  private readonly bridgeCommand: string;
  private readonly databasePath: string;
  private readonly llmModel?: string;
  private readonly bridgeArgs: string[];
  private readonly timeoutMs: number;
  private readonly maxBufferBytes: number;

  constructor(options: ProcessBridgeTransportOptions = {}) {
    this.bridgeCommand = options.bridgeCommand ?? 'memory-sdk-bridge';
    this.databasePath = options.databasePath ?? './memory.db';
    this.llmModel = options.llmModel?.trim() || undefined;
    this.bridgeArgs = [...(options.bridgeArgs ?? [])];
    this.timeoutMs = options.timeoutMs ?? 30_000;
    this.maxBufferBytes = options.maxBufferBytes ?? 1024 * 1024;
    for (const value of [this.timeoutMs, this.maxBufferBytes]) {
      if (!Number.isSafeInteger(value) || value < 1) {
        throw new RangeError('transport limits must be positive safe integers');
      }
    }
  }

  async execute(request: BridgeRequest): Promise<BridgeResponse> {
    const args = [...this.bridgeArgs, '--db', this.databasePath];
    if (this.llmModel) {
      args.push('--llm-model', this.llmModel);
    }

    const output = await new Promise<string>((resolve, reject) => {
      const child = execFile(this.bridgeCommand, args, {
        encoding: 'utf8', shell: false, windowsHide: true,
        timeout: this.timeoutMs, maxBuffer: this.maxBufferBytes, killSignal: 'SIGKILL',
      }, (error, stdout) => {
        if (error) reject(error);
        else resolve(stdout);
      });
      child.stdin?.on('error', () => { /* execFile reports child failures in its callback. */ });
      child.stdin?.end(JSON.stringify(request));
    });
    const stdout = output.trim();
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
