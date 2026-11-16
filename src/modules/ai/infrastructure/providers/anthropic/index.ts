import { AIProvider, AIModel, TranslationRequest, TranslationResponse } from "../../../domain/interfaces/ai-provider";

export class AnthropicProvider implements AIProvider {
  id: string = "anthropic";
  name: string = "Anthropic";
  type: "commercial" | "local" = "commercial";
  private apiKey: string;
  private baseUrl: string = "https://api.anthropic.com";

  constructor(config: { apiKey: string; baseUrl?: string }) {
    this.apiKey = config.apiKey;
    if (config.baseUrl) this.baseUrl = config.baseUrl;
  }

  async validateConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/v1/models`, {
        method: "GET",
        headers: {
          "x-api-key": this.apiKey,
          "anthropic-version": "2023-06-01",
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async listModels(): Promise<AIModel[]> {
    const response = await fetch(`${this.baseUrl}/v1/models`, {
      method: "GET",
      headers: {
        "x-api-key": this.apiKey,
        "anthropic-version": "2023-06-01",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to list Anthropic models");
    }

    const models = await response.json();
    return models.data.map((m: any) => ({
      id: m.id,
      name: m.name || m.id,
      provider: "anthropic",
      contextWindow: this.getContextWindow(m.id),
      capabilities: this.getCapabilities(m.id),
      isDefault: m.id.includes("claude-3") || m.id.includes("claude-2"),
      supportsStructuredOutput: m.id.includes("claude-3"),
      supportsSystemPrompt: true,
      supportsTemperature: true,
      supportsTopP: true,
    }));
  }

  async translate(request: TranslationRequest): Promise<TranslationResponse> {
    const model = await this.listModels();
    const modelId = model.find((m) => m.isDefault)?.id || request.modelId || "claude-3-haiku-20240307";

    const systemPrompt = this.getSystemPrompt(request.preserveTechnicalTerms);

    const messages: any[] = [
      { role: "user", content: this.buildPrompt(request) },
    ];

    const payload = {
      model: modelId,
      system: systemPrompt,
      messages,
      temperature: request.context?.temperature,
      max_tokens: request.context?.maxTokens,
      stop_sequences: ["\n\nHuman:"],
    };

    const response = await fetch(`${this.baseUrl}/v1/messages`, {
      method: "POST",
      headers: {
        "x-api-key": this.apiKey,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      return {
        success: false,
        translatedText: "",
        error: {
          message: `Erro na API Anthropic: ${errorBody}`,
          type: "api_error",
          code: undefined,
        },
      };
    }

    const data = await response.json();
    const text =
      typeof data.content === "array"
        ? data.content
            .filter((c: any) => c.type === "text")
            .map((c: any) => c.text)
            .join("\n")
        : data.content;

    return {
      success: true,
      translatedText: text || "",
      usage: {
        promptTokens: data.usage?.input_tokens || 0,
        completionTokens: data.usage?.output_tokens || 0,
        totalTokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0),
      },
    };
  }

  async getCapabilities(modelId: string): Promise<{
    supportsStructuredOutput: boolean;
    supportsSystemPrompt: boolean;
    maxContextTokens: number;
    supportsTemperature: boolean;
    supportsTopP: boolean;
  }> {
    const isClaude3 = modelId.includes("claude-3");

    return Promise.resolve({
      supportsStructuredOutput: isClaude3,
      supportsSystemPrompt: true,
      maxContextTokens: isClaude3 ? 100000 : 100000,
      supportsTemperature: true,
      supportsTopP: true,
    })
  }

  private getSystemPrompt(preserveTechnicalTerms: boolean): string {
    const technicalTermsInstructions = preserveTechnicalTerms
      ? "\n10. Preservar nomenclaturas técnicas, siglas, nomes próprios e identificadores quando apropriado."
      : "";

    return `Instruções de tradução:

1. Traduzir preservando integralmente o significado original.
2. Não resumir, simplificar ou omitir informações.
3. Não adicionar explicações inexistentes no original.
4. Preservar nomenclaturas técnicas quando apropriado${technicalTermsInstructions}.
5. Preservar siglas, nomes próprios e identificadores.
6. Respeitar o contexto dos parágrafos anteriores e posteriores.
7. Não modificar números, datas, unidades ou valores sem necessidade linguística explícita.
8. Retornar apenas o texto traduzido, sem cabeçalhos ou comentários adicionais.`;
  }

  private buildPrompt(request: TranslationRequest): string {
    const parts: string[] = [];

    parts.push(`Traduzir do idioma ${request.sourceLanguage} para ${request.targetLanguage}`);

    if (request.context) {
      parts.push(`Contexto: ${request.context}`);
    }

    parts.push(`Texto: ${request.prompt}`);

    if (request.preserveTechnicalTerms) {
      parts.push("\nIMPORTANTE: Preservar termos técnicos, siglas e nomes próprios.");
    }

    return parts.join("\n");
  }

  private getContextWindow(modelId: string): number {
    if (modelId.includes("sonnet")) return 200000;
    if (modelId.includes("opus")) return 200000;
    if (modelId.includes("haiku")) return 8192;
    return 100000;
  }

}