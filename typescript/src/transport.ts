import type { BridgeRequest, BridgeResponse } from './types.js';

export interface MemoryTransport {
  execute(request: BridgeRequest): Promise<BridgeResponse>;
}
