import { spawnSync } from 'node:child_process';

import type {
  IDataObject,
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  NodeConnectionType,
} from 'n8n-workflow';
import { NodeOperationError } from 'n8n-workflow';

type BridgePayload = Record<string, unknown>;

const mainConnection: NodeConnectionType = 'main';

function runBridge(
  bridgeCommand: string,
  databasePath: string,
  llmModel: string,
  payload: BridgePayload,
): IDataObject {
  const args = ['--db', databasePath];
  if (llmModel.trim()) {
    args.push('--llm-model', llmModel.trim());
  }

  const result = spawnSync(bridgeCommand, args, {
    input: JSON.stringify(payload),
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

  const parsed: unknown = JSON.parse(stdout);
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new Error('memory-sdk bridge returned an invalid JSON response');
  }
  return parsed as IDataObject;
}

export class AiMemory implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'AI Memory SDK',
    name: 'aiMemory',
    icon: 'file:aiMemory.svg',
    group: ['transform'],
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description: 'Use the local-first AI Memory SDK from self-hosted n8n',
    defaults: {
      name: 'AI Memory SDK',
    },
    inputs: [mainConnection],
    outputs: [mainConnection],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        noDataExpression: true,
        options: [
          { name: 'Save', value: 'save', description: 'Save text or a structured memory', action: 'Save memory' },
          { name: 'Retrieve', value: 'retrieve', description: 'Retrieve ranked memories for a user', action: 'Retrieve memories' },
          { name: 'Search', value: 'search', description: 'Semantically search memories for a user', action: 'Search memories' },
          { name: 'Forget', value: 'forget', description: 'Delete one user-scoped memory', action: 'Forget memory' },
        ],
        default: 'save',
      },
      {
        displayName: 'Bridge Command',
        name: 'bridgeCommand',
        type: 'string',
        default: 'memory-sdk-bridge',
        description: 'Executable name or absolute path for the installed Python bridge',
      },
      {
        displayName: 'Database Path',
        name: 'databasePath',
        type: 'string',
        default: './memory.db',
        description: 'Path to the local SQLite memory database as seen by the n8n process',
      },
      {
        displayName: 'User ID',
        name: 'userId',
        type: 'string',
        default: '',
        required: true,
        description: 'Stable application user identifier used to isolate memories',
      },
      {
        displayName: 'Save Mode',
        name: 'saveMode',
        type: 'options',
        options: [
          { name: 'Text', value: 'text' },
          { name: 'Structured', value: 'structured' },
        ],
        default: 'text',
        displayOptions: { show: { operation: ['save'] } },
      },
      {
        displayName: 'Text',
        name: 'text',
        type: 'string',
        typeOptions: { rows: 4 },
        default: '',
        required: true,
        displayOptions: { show: { operation: ['save'], saveMode: ['text'] } },
        description: 'Unstructured text to extract durable memories from',
      },
      {
        displayName: 'LiteLLM Model',
        name: 'llmModel',
        type: 'string',
        default: '',
        displayOptions: { show: { operation: ['save'], saveMode: ['text'] } },
        description: 'LiteLLM model identifier used by text Save, for example openai/gpt-4.1-mini',
      },
      {
        displayName: 'Key',
        name: 'key',
        type: 'string',
        default: '',
        required: true,
        displayOptions: { show: { operation: ['save'], saveMode: ['structured'] } },
      },
      {
        displayName: 'Value',
        name: 'value',
        type: 'string',
        default: '',
        required: true,
        displayOptions: { show: { operation: ['save'], saveMode: ['structured'] } },
      },
      {
        displayName: 'Kind',
        name: 'kind',
        type: 'string',
        default: 'fact',
        displayOptions: { show: { operation: ['save'], saveMode: ['structured'] } },
      },
      {
        displayName: 'Importance',
        name: 'importance',
        type: 'number',
        typeOptions: { minValue: 0, maxValue: 1, numberPrecision: 2 },
        default: 0.5,
        displayOptions: { show: { operation: ['save'], saveMode: ['structured'] } },
      },
      {
        displayName: 'Query',
        name: 'query',
        type: 'string',
        default: '',
        required: true,
        displayOptions: { show: { operation: ['search'] } },
      },
      {
        displayName: 'Limit',
        name: 'limit',
        type: 'number',
        typeOptions: { minValue: 1, maxValue: 100 },
        default: 10,
        displayOptions: { show: { operation: ['retrieve', 'search'] } },
      },
      {
        displayName: 'Memory ID',
        name: 'memoryId',
        type: 'string',
        default: '',
        required: true,
        displayOptions: { show: { operation: ['forget'] } },
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const returnData: INodeExecutionData[] = [];

    for (let itemIndex = 0; itemIndex < items.length; itemIndex += 1) {
      try {
        const operation = this.getNodeParameter('operation', itemIndex) as string;
        const bridgeCommand = this.getNodeParameter('bridgeCommand', itemIndex) as string;
        const databasePath = this.getNodeParameter('databasePath', itemIndex) as string;
        const userId = this.getNodeParameter('userId', itemIndex) as string;
        const payload: BridgePayload = { operation, userId };
        let llmModel = '';

        if (operation === 'save') {
          const saveMode = this.getNodeParameter('saveMode', itemIndex) as string;
          if (saveMode === 'text') {
            payload.text = this.getNodeParameter('text', itemIndex) as string;
            llmModel = this.getNodeParameter('llmModel', itemIndex) as string;
          } else {
            payload.key = this.getNodeParameter('key', itemIndex) as string;
            payload.value = this.getNodeParameter('value', itemIndex) as string;
            payload.kind = this.getNodeParameter('kind', itemIndex) as string;
            payload.importance = this.getNodeParameter('importance', itemIndex) as number;
          }
        } else if (operation === 'retrieve') {
          payload.limit = this.getNodeParameter('limit', itemIndex) as number;
        } else if (operation === 'search') {
          payload.query = this.getNodeParameter('query', itemIndex) as string;
          payload.limit = this.getNodeParameter('limit', itemIndex) as number;
        } else if (operation === 'forget') {
          payload.memoryId = this.getNodeParameter('memoryId', itemIndex) as string;
        }

        const response = runBridge(bridgeCommand, databasePath, llmModel, payload);
        returnData.push({ json: response, pairedItem: { item: itemIndex } });
      } catch (error) {
        if (this.continueOnFail()) {
          returnData.push({
            json: { error: error instanceof Error ? error.message : String(error) },
            pairedItem: { item: itemIndex },
          });
          continue;
        }
        throw new NodeOperationError(this.getNode(), error as Error, { itemIndex });
      }
    }

    return [returnData];
  }
}
