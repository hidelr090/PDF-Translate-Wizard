export interface AIModel {
  id: string;
  name: string;
  provider: string;
  contextWindow: number;
  capabilities: string[];
  isDefault: boolean;
  supportsStructuredOutput: boolean;
  supportsSystemPrompt: boolean;
  supportsTemperature: boolean;
  supportsTopP: boolean;
}

export interface TranslationRequest {
  id?: string;
  prompt: string;
  modelId: string;
  sourceLanguage: string;
  targetLanguage: string;
  context?: {
    temperature?: number;
    topP?: number;
    maxTokens?: number;
    preserveTechnicalTerms?: boolean;
  };
  preserveTechnicalTerms: boolean;
  glossaryTerms?: string[];
}

export interface TranslationResponse {
  id?: string;
  success: boolean;
  translatedText: string;
  usage?: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  error?: {
    message: string;
    type: string;
    code?: string;
  };
  rawResponse?: any;
}

export interface AIProvider {
  id: string;
  name: string;
  type: 'commercial' | 'local';

  validateConnection(): Promise<boolean>;
  listModels(): Promise<AIModel[]>;
  translate(request: TranslationRequest): Promise<TranslationResponse>;
  getCapabilities(modelId: string): Promise<{
    supportsStructuredOutput: boolean;
    supportsSystemPrompt: boolean;
    maxContextTokens: number;
    supportsTemperature: boolean;
    supportsTopP: boolean;
  }>;
}

export interface ProviderConfig {
  id: string;
  name: string;
  type: 'commercial' | 'local';
  apiKey?: string;
  baseUrl?: string;
  isActive: boolean;
  createdAt: string;
}

export interface ProviderManagerEvents {
  connectionChanged: (providerId: string, isConnected: boolean) => void;
  modelsLoaded: (providerId: string, models: AIModel[]) => void;
  translationProgress: (jobId: string, progress: number) => void;
  translationComplete: (jobId: string, response: TranslationResponse) => void;
  translationError: (jobId: string, error: Error) => void;
}