import type { MemoryTransport } from './transport.js';
import type {
  BridgeResponse,
  ForgetInput,
  MemoryFact,
  RetrieveOptions,
  SaveInput,
  SearchInput,
} from './types.js';

function memoryResponse(response: BridgeResponse): MemoryFact[] {
  if (!('memories' in response) || !Array.isArray(response.memories)) {
    throw new Error('memory transport returned a response without memories');
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
      }),
    );
  }

  async forget(input: ForgetInput): Promise<boolean> {
    const response = await this.transport.execute({
      operation: 'forget',
      userId: input.userId,
      memoryId: input.memoryId,
    });
    if (!('forgotten' in response) || typeof response.forgotten !== 'boolean') {
      throw new Error('memory transport returned a response without forgotten status');
    }
    return response.forgotten;
  }
}
