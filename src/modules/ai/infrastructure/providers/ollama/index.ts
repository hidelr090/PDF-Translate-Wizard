import { AIProvider, AIModel, TranslationRequest, TranslationResponse } from "../../../domain/interfaces/ai-provider";

export class OllamaProvider implements AIProvider {
  private baseUrl: string;
  private readonly providerId = "ollama";

  constructor(config: { baseUrl?: string }) {
    this.baseUrl = config.baseUrl || "http://localhost:11434";
  }

  async validateConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, { method: "GET", timeout: 5000 });
      return response.ok;
    } catch {
      return false;
    }
  }

  async listModels(): Promise<AIModel[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, { method: "GET", timeout: 10000 });
      if (!response.ok) throw new Error("Failed to list Ollama models");
      const data = await response.json();
      return data.models.map((m: any) => ({
        id: m.name,
        name: m.name,
        provider: "ollama",
        contextWindow: this.estimateContextWindow(m.name),
        capabilities: this.estimateCapabilities(m.name),
        isDefault: this.isDefaultModel(m.name),
        supportsStructuredOutput: this.supportsStructuredOutput(m.name),
        supportsSystemPrompt: true,
        supportsTemperature: true,
        supportsTopP: true,
      }));
    } catch (error) {
      console.error("Error listing Ollama models:", error);
      return [];
    }
  }

  async translate(request: TranslationRequest): Promise<TranslationResponse> {
    const models = await this.listModels();
    const modelId = models.find((m) => m.isDefault)?.id || request.modelId || this.getFirstAvailableModel(models);

    if (!modelId) {
      return { success: false, translatedText: "", error: new Error("Nenhum modelo Ollama disponível") };
    }

    const systemPrompt = this.getSystemPrompt(request.preserveTechnicalTerms);
    const payload = {
      model: modelId,
      prompt: this.buildFullPrompt(request, modelId),
      stream: false,
      options: { temperature: request.context?.temperature, top_p: request.context?.topP, num_predict: request.context?.maxTokens },
    };

    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), timeout: 120000 });
      if (!response.ok) {
        const errorText = await response.text();
        return { success: false, translatedText: "", error: { message: `Erro na API Ollama: ${errorText}`, type: "api_error", code: undefined } };
      }
      const data = await response.json();
      const text = data.message?.content || data.response || "";
      return { success: true, translatedText: text || "", usage: { promptTokens: data.prompt_eval_count || 0, completionTokens: data.eval_count || 0, totalTokens: (data.prompt_eval_count || 0) + (data.eval_count || 0) } };
    } catch (error: any) {
      return { success: false, translatedText: "", error: { message: `Erro na comunicação com Ollama: ${error.message}`, type: "connection_error", code: undefined } };
    }
  }

  getCapabilities(modelId: string): { supportsStructuredOutput: boolean; supportsSystemPrompt: boolean; maxContextTokens: number; supportsTemperature: boolean; supportsTopP: boolean } {
    return { supportsStructuredOutput: this.supportsStructuredOutput(modelId), supportsSystemPrompt: true, maxContextTokens: this.estimateContextWindow(modelId), supportsTemperature: true, supportsTopP: true };
  }

  private estimateContextWindow(modelName: string): number {
    const lower = modelName.toLowerCase();
    if (lower.contains("llama3")) return 8192;
    if (lower.contains("mixtral")) return 32768;
    if (lower.contains("phi")) return 2048;
    if (lower.contains("nemotron")) return 4096;
    return 4096;
  }

  private supportsStructuredOutput(modelName: string): boolean {
    const lower = modelName.toLowerCase();
    return lower.contains("llama3") || lower.contains("mixtral");
  }

  private isDefaultModel(modelName: string): boolean {
    const lower = modelName.toLowerCase();
    return lower.contains("llama3") || lower.contains("default");
  }

  private getFirstAvailableModel(models: AIModel[]): string | undefined {
    return models.find((m) => m.isDefault)?.id || models[0]?.id;
  }

  private getSystemPrompt(preserveTechnicalTerms: boolean): string {
    const technicalTermsInstructions = preserveTechnicalTerms ? "\n10. Preservar nomenclaturas técnicas, siglas, nomes próprios e identificadores quando apropriado." : "";
    return `Tradutor de documentos PDF via IA Local (Ollama):

1. Traduzir preservando integralmente o significado original.
2. Não resumir, simplificar ou omitir informações.
3. Não adicionar explicações inexistentes no original.
4. Preservar nomenclaturas técnicas quando apropriado${technicalTermsInstructions}.
5. Preservar siglas, nomes próprios e identificadores.
6. Respeitar o contexto dos parágrafos anteriores e posteriores.
7. Não modificar números, datas, unidades ou valores sem necessidade linguística explícita.
8. Retornar apenas o texto traduzido, sem comentários ou metadados adicionais.`;
  }

  private buildFullPrompt(request: TranslationRequest, modelId: string): string {
    const parts: string[] = [];
    parts.push(`Traduzir do idioma ${request.sourceLanguage} para ${request.targetLanguage}`);
    if (request.context) { parts.push(`Contexto: ${request.context}`); }
    parts.push(`Texto a traduzir:`);
    parts.push(request.prompt);
    if (request.preserveTechnicalTerms) { parts.push("\nIMPORTANTE: Preservar termos técnicos, siglas e nomes próprios."); }
    return parts.join("\n");
  }

  private estimateCapabilities(modelName: string): string[] {
    const lower = modelName.toLowerCase();
    if (lower.contains("llama3")) return ["temperature", "top_p"];
    if (lower.contains("mixtral")) return ["temperature", "top_p", "repeat_penalty"];
    return ["temperature"];
  }
}