export interface MemoryFact {
  id: string;
  user_id: string;
  kind: string;
  key: string;
  value: string;
  importance: number;
  embedding: number[] | null;
  created_at: string;
  updated_at: string;
}

export interface TextSaveInput {
  userId: string;
  text: string;
}

export interface StructuredSaveInput {
  userId: string;
  key: string;
  value: string;
  kind?: string;
  importance?: number;
}

export type SaveInput = TextSaveInput | StructuredSaveInput;

export interface RetrieveOptions {
  limit?: number;
}

export interface SearchInput {
  userId: string;
  query: string;
  limit?: number;
}

export interface ForgetInput {
  userId: string;
  memoryId: string;
}

export type BridgeRequest =
  | { operation: 'save'; userId: string; text: string }
  | {
      operation: 'save';
      userId: string;
      key: string;
      value: string;
      kind?: string;
      importance?: number;
    }
  | { operation: 'retrieve'; userId: string; limit?: number }
  | { operation: 'search'; userId: string; query: string; limit?: number }
  | { operation: 'forget'; userId: string; memoryId: string };

export interface MemoryListResponse {
  memories: MemoryFact[];
}

export interface ForgetResponse {
  forgotten: boolean;
}

export type BridgeResponse = MemoryListResponse | ForgetResponse;
