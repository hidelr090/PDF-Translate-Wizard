import { AIProvider, AIModel, TranslationRequest, TranslationResponse } from "../../../domain/interfaces/ai-provider";

export class OpenAIProvider implements AIProvider {
  private apiKey: string;
  private baseUrl: string = "https://api.openai.com/v1";
  private readonly providerId = "openai";

  constructor(config: { apiKey: string; baseUrl?: string }) {
    this.apiKey = apiKey;
    if (baseUrl) this.baseUrl = baseUrl;
  }

  async validateConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/models`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${this.apiKey}`,
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async listModels(): Promise<AIModel[]> {
    const response = await fetch(`${this.baseUrl}/models`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to list models");
    }

    const models = await response.json();
    return models.data.map((m: any) => ({
      id: m.id,
      name: m.id,
      provider: "openai",
      contextWindow: this.getContextWindow(m.id),
      capabilities: this.getCapabilities(m.id),
      isDefault: m.id.startsWith("gpt-4") || m.id.startsWith("gpt-3.5"),
      supportsStructuredOutput: true,
      supportsSystemPrompt: true,
      supportsTemperature: true,
      supportsTopP: true,
    }));
  }

  async translate(request: TranslationRequest): Promise<TranslationResponse> {
    const model = await this.listModels();
    const modelId = model.find((m) => m.isDefault)?.id || request.modelId || "gpt-4o-mini";

    const systemPrompt = this.getSystemPrompt(request.preserveTechnicalTerms);

    const messages: any[] = [
      { role: "system", content: systemPrompt },
      { role: "user", content: this.buildPrompt(request) },
    ];

    const payload = {
      model: modelId,
      messages,
      temperature: request.context?.temperature,
      max_tokens: request.context?.maxTokens,
      response_format: { type: "text" },
    };

    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorBody = await response.json();
      return {
        success: false,
        translatedText: "",
        error: {
          message: errorBody.error?.message || "Erro na API OpenAI",
          type: errorBody.error?.type || "api_error",
          code: errorBody.error?.code,
        },
      };
    }

    const data = await response.json();
    const text = data.choices[0]?.message?.content || "";

    return {
      success: true,
      translatedText: text,
      usage: {
        promptTokens: data.usage?.prompt_tokens || 0,
        completionTokens: data.usage?.completion_tokens || 0,
        totalTokens: data.usage?.total_tokens || 0,
      },
    };
  }

  getCapabilities(modelId: string): {
    supportsStructuredOutput: boolean;
    supportsSystemPrompt: boolean;
    maxContextTokens: number;
    supportsTemperature: boolean;
    supportsTopP: boolean;
  } {
    const isGpt4 = modelId.startsWith("gpt-4");
    const isGpt35 = modelId.startsWith("gpt-3.5");

    return {
      supportsStructuredOutput: isGpt4,
      supportsSystemPrompt: true,
      maxContextTokens: isGpt4 ? 8192 : 4096,
      supportsTemperature: true,
      supportsTopP: isGpt4 || isGpt35,
    };
  }

  private getSystemPrompt(preserveTechnicalTerms: boolean): string {
    const technicalTermsInstructions = preserveTechnicalTerms
      ? "\n10. Preservar nomenclaturas técnicas, siglas, nomes próprios e identificadores quando apropriado."
      : "";

    return `Você é um tradutor especializado. Instruções fundamentais:

1. Traduzir preservando integralmente o significado original.
2. Não resumir, simplificar ou omitir informações.
3. Não adicionar explicações inexistentes no original.
4. Preservar nomenclaturas técnicas quando apropriado${technicalTermsInstructions}.
5. Preservar siglas, nomes próprios e identificadores.
6. Respeitar o contexto dos parágrafos anteriores e posteriores.
7. Não modificar números, datas, unidades ou valores sem necessidade linguística explícita.
8. Retornar exatamente o texto traduzido, sem comentários adicionais.`;
  }

  private buildPrompt(request: TranslationRequest): string {
    const parts: string[] = [];

    parts.push(`Traduzir do idioma ${request.sourceLanguage} para ${request.targetLanguage}:`);

    if (request.context) {
      parts.push(`Contexto: ${request.context}`);
    }

    parts.push(`Texto a traduzir: ${request.prompt}`);

    if (request.preserveTechnicalTerms) {
      parts.push("\nIMPORTANTE: Preservar termos técnicos, siglas e nomes próprios.");
    }

    return parts.join("\n");
  }

  private getContextWindow(modelId: string): number {
    if (modelId.includes("4")) return 8192;
    if (modelId.includes("3.5")) return 16385;
    return 4096;
  }

  private getCapabilities(modelId: string): string[] {
    if (modelId.includes("4")) return ["structured_output", "system_prompt", "temperature", "top_p"];
    if (modelId.includes("3.5")) return ["temperature", "top_p"];
    return ["temperature"];
  }
}