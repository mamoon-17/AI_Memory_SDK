export type BridgeErrorCode = 'TIMEOUT' | 'OUTPUT_LIMIT' | 'PROCESS' | 'PROTOCOL';

export class BridgeError extends Error {
  constructor(public readonly code: BridgeErrorCode, message: string, cause?: unknown) {
    super(message, { cause });
    this.name = 'BridgeError';
  }
}
