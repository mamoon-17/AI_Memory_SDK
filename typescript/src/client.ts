import type { MemoryTransport } from './transport.js';
import { BridgeError } from './errors.js';
import { isMemoryFact, isRecord } from './validation.js';
import type {
  ForgetInput,
  MemoryFact,
  RetrieveOptions,
  SaveInput,
  SearchInput,
} from './types.js';

function memoryResponse(response: unknown): MemoryFact[] {
  if (!isRecord(response) || !Array.isArray(response.memories)) {
    throw new BridgeError('PROTOCOL', 'memory transport returned a response without memories');
  }
  if (!response.memories.every(isMemoryFact)) {
    throw new BridgeError('PROTOCOL', 'memory transport returned an invalid memory record');
  }
  return response.memories;
}

export class MemoryClient {
  constructor(private readonly transport: MemoryTransport) {}

  async save(input: SaveInput): Promise<MemoryFact[]> {
    if ('text' in input) {
      return memoryResponse(
        await this.transport.execute({
          operation: 'save',
          userId: input.userId,
          text: input.text,
        }),
      );
    }

    return memoryResponse(
      await this.transport.execute({
        operation: 'save',
        userId: input.userId,
        key: input.key,
        value: input.value,
        ...(input.kind === undefined ? {} : { kind: input.kind }),
        ...(input.importance === undefined ? {} : { importance: input.importance }),
      }),
    );
  }

  async retrieve(userId: string, options: RetrieveOptions = {}): Promise<MemoryFact[]> {
    return memoryResponse(
      await this.transport.execute({
        operation: 'retrieve',
        userId,
        ...(options.limit === undefined ? {} : { limit: options.limit }),
        ...(options.filters === undefined ? {} : { filters: options.filters }),
      }),
    );
  }

  async search(input: SearchInput): Promise<MemoryFact[]> {
    return memoryResponse(
      await this.transport.execute({
        operation: 'search',
        userId: input.userId,
        query: input.query,
        ...(input.limit === undefined ? {} : { limit: input.limit }),
        ...(input.filters === undefined ? {} : { filters: input.filters }),
        ...(input.mode === undefined ? {} : { mode: input.mode }),
      }),
    );
  }

  async forget(input: ForgetInput): Promise<boolean> {
    const response = await this.transport.execute({
      operation: 'forget',
      userId: input.userId,
      memoryId: input.memoryId,
    });
    if (!isRecord(response) || typeof response.forgotten !== 'boolean') {
      throw new BridgeError('PROTOCOL', 'memory transport returned a response without forgotten status');
    }
    return response.forgotten;
  }
}
