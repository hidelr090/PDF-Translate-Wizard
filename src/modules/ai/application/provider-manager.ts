import { AIProvider, AIModel, TranslationRequest, TranslationResponse, ProviderConfig } from "../../domain/interfaces/ai-provider";

export class ProviderManager {
  private providers: Map<string, AIProvider> = new Map();
  private configs: Map<string, ProviderConfig> = new Map();

  constructor() {
    this.loadDefaultConfigs();
  }

  private loadDefaultConfigs(): void {
    const defaultConfigs: ProviderConfig[] = [
      { id: "openai", name: "OpenAI", type: "commercial", isActive: true },
      { id: "anthropic", name: "Anthropic Claude", type: "commercial", isActive: true },
      { id: "gemini", name: "Google Gemini", type: "commercial", isActive: true },
      { id: "ollama", name: "Ollama (Local)", type: "local", isActive: true },
    ];
    for (const config of defaultConfigs) {
      this.configs.set(config.id, config);
    }
  }

  getConfig(providerId: string): ProviderConfig | undefined {
    return this.configs.get(providerId);
  }

  setConfig(config: ProviderConfig): void {
    this.configs.set(config.id, config);
  }

  async validateConnection(providerId: string): Promise<boolean> {
    const provider = this.providers.get(providerId);
    if (!provider) return false;
    return await provider.validateConnection();
  }

  async listModels(providerId: string): Promise<AIModel[]> {
    const provider = this.providers.get(providerId);
    if (!provider) return [];
    return await provider.listModels();
  }

  async translate(
    providerId: string,
    request: TranslationRequest
  ): Promise<TranslationResponse> {
    const provider = this.providers.get(providerId);
    if (!provider) {
      return {
        success: false,
        translatedText: "",
        error: new Error("Provedor não configurado"),
      };
    }
    try {
      const response = await provider.translate(request);
      return response;
    } catch (error: any) {
      return {
        success: false,
        translatedText: "",
        error,
      };
    }
  }

  registerProvider(provider: AIProvider, config: ProviderConfig): void {
    this.providers.set(config.id, provider);
    this.configs.set(config.id, config);
  }

  unregisterProvider(providerId: string): void {
    this.providers.delete(providerId);
  }

  getActiveProviders(): ProviderConfig[] {
    return Array.from(this.configs.values()).filter((c) => c.isActive);
  }

  getAllProviders(): AIProvider[] {
    return Array.from(this.providers.values());
  }
}
