import { AIProvider, AIModel, TranslationRequest, TranslationResponse, ProviderConfig } from "../../domain/interfaces/ai-provider";
import { SegmentadorUseCase } from "../translation/application/use-cases/segmentar-use-case";
import { GlossaryTerm } from "../domain/interfaces/translation-engine";

export class ProviderManager {
  private providers: Map<string, AIProvider> = new Map();
  private configs: Map<string, ProviderConfig> = new Map();
  private segmentador: SegmentadorUseCase | null = null;

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

  setSegmentador(config: { respectTechnicalTerms: boolean; useGlossary: boolean; allowPageExpansion: boolean; maxConcurrentRequests: number; retryAttempts: number; retryDelay: number }): void {
    this.segmentador = new SegmentadorUseCase({
      respectColumnBreaks: true,
      preserveParagraphs: true,
      maxTokensPerSegment: 2000,
      includeContext: true,
      contextLines: 1,
      ...config,
    });
  }

  getSegmentador(): SegmentadorUseCase | null {
    return this.segmentador;
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

  async traduzirComSegmentacao(
    providerId: string,
    request: TranslationRequest,
    glossaryTerms: GlossaryTerm[] = []
  ): Promise<TranslationResponse> {
    if (!this.segmentador) {
      return this.translate(providerId, request);
    }

    // 1. Obter modelos disponíveis
    const models = await this.listModels(providerId);
    if (!models.length) {
      return {
        success: false,
        translatedText: "",
        error: new Error("Nenhum modelo disponível para o provedor"),
      };
    }

    // 2. Selecionar modelo padrão
    const modelId = models.find((m) => m.isDefault)?.id || request.modelId || this.obterPrimeiroModelo(models);

    // 3. Build prompt com contexto e glossário
    const systemPrompt = this.segmentador.config.respectTechnicalTerms
      ? "Preservar nomenclaturas técnicas, siglas e nomes próprios."
      : "";

    const contextLines = this.segmentador.config.contextLines;
    let context = "";
    if (contextLines > 0 && request.context) {
      context = `Contexto anterior/posterior (${contextLines} linhas): ${request.context}\n\n`;
    }

    const glossaryInstructions = this.segmentador.config.useGlossary && glossaryTerms.length > 0
      ? `\nGlossário obrigatório: ${glossaryTerms.map(t => `${t.term} -> ${t.translation}`).join("; ")}`
      : "";

    const fullPrompt = `${systemPrompt}

${context}Traduzir do idioma ${request.sourceLanguage} para ${request.targetLanguage}:

${request.prompt}${glossaryInstructions}

Instruções:
1. Traduzir preservando integralmente o significado original
2. Não resumir, simplificar ou omitir informações
3. Não adicionar explicações inexistentes no original
4. Preservar nomenclaturas técnicas quando apropriado
5. Preservar siglas, nomes próprios e identificadores
6. Respeitar o contexto dos parágrafos anteriores e posteriores
7. Não modificar números, datas, unidades ou valores sem necessidade linguística explícita
8. Retornar apenas o texto traduzido, sem comentários adicionais`;

    // 3. Executar tradução
    const response = await this.translate(providerId, {
      ...request,
      context: fullPrompt,
    });

    // 4. Aplicar glossário se configurado
    if (this.segmentador.config.useGlossary && glossaryTerms.length > 0 && response.success) {
      response.translatedText = this.segmentador.aplicarGlossario(
        [{ originalText: request.prompt, translatedText: response.translatedText, status: "translated", id: "current", order: 0, pageNumber: 0, boundingBox: { x0: 0, y0: 0, x1: 0, y1: 0 } }],
        glossaryTerms
      )[0].translatedText;
    }

    return response;
  }

  private obterPrimeiroModelo(models: AIModel[]): string | undefined {
    return models.find((m) => m.isDefault)?.id || models[0]?.id;
  }
}
