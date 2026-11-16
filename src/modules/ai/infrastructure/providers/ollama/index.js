export class OllamaProvider {
    id = "ollama";
    name = "Ollama";
    type = "local";
    baseUrl;
    constructor(config) {
        this.baseUrl = config.baseUrl || "http://localhost:11434";
    }
    async validateConnection() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000);
            const response = await fetch(`${this.baseUrl}/api/tags`, { method: "GET", signal: controller.signal });
            clearTimeout(timeoutId);
            return response.ok;
        }
        catch (error) {
            if (error instanceof DOMException && error.name === "AbortError") {
                return false;
            }
            return false;
        }
    }
    async listModels() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);
            const response = await fetch(`${this.baseUrl}/api/tags`, { method: "GET", signal: controller.signal });
            clearTimeout(timeoutId);
            if (!response.ok)
                throw new Error("Failed to list Ollama models");
            const data = await response.json();
            return data.models.map((m) => ({
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
        }
        catch (error) {
            console.error("Error listing Ollama models:", error);
            return [];
        }
    }
    async translate(request) {
        const models = await this.listModels();
        const modelId = models.find((m) => m.isDefault)?.id || request.modelId || this.getFirstAvailableModel(models);
        if (!modelId) {
            return { success: false, translatedText: "", error: new Error("Nenhum modelo Ollama disponível") };
        }
        const payload = {
            model: modelId,
            prompt: this.buildFullPrompt(request, modelId),
            stream: false,
            options: { temperature: request.context?.temperature, top_p: request.context?.topP, num_predict: request.context?.maxTokens, system: this.getSystemPrompt(request.preserveTechnicalTerms) },
        };
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 120000);
            const response = await fetch(`${this.baseUrl}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(timeoutId);
            if (!response.ok) {
                const errorText = await response.text();
                return { success: false, translatedText: "", error: { message: `Erro na API Ollama: ${errorText}`, type: "api_error", code: undefined } };
            }
            const data = await response.json();
            const text = data.message?.content || data.response || "";
            return { success: true, translatedText: text || "", usage: { promptTokens: data.prompt_eval_count || 0, completionTokens: data.eval_count || 0, totalTokens: (data.prompt_eval_count || 0) + (data.eval_count || 0) } };
        }
        catch (error) {
            if (error instanceof DOMException && error.name === "AbortError") {
                return { success: false, translatedText: "", error: { message: "Timeout na comunicação com Ollama", type: "timeout", code: undefined } };
            }
            return { success: false, translatedText: "", error: { message: `Erro na comunicação com Ollama: ${error.message}`, type: "connection_error", code: undefined } };
        }
    }
    async getCapabilities(modelId) {
        return Promise.resolve({ supportsStructuredOutput: this.supportsStructuredOutput(modelId), supportsSystemPrompt: true, maxContextTokens: this.estimateContextWindow(modelId), supportsTemperature: true, supportsTopP: true });
    }
    estimateContextWindow(modelName) {
        const lower = modelName.toLowerCase();
        if (lower.includes("llama3"))
            return 8192;
        if (lower.includes("mixtral"))
            return 32768;
        if (lower.includes("phi"))
            return 2048;
        if (lower.includes("nemotron"))
            return 4096;
        return 4096;
    }
    supportsStructuredOutput(modelName) {
        const lower = modelName.toLowerCase();
        return lower.includes("llama3") || lower.includes("mixtral");
    }
    isDefaultModel(modelName) {
        const lower = modelName.toLowerCase();
        return lower.includes("llama3") || lower.includes("default");
    }
    getFirstAvailableModel(models) {
        return models.find((m) => m.isDefault)?.id || models[0]?.id;
    }
    getSystemPrompt(preserveTechnicalTerms) {
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
    buildFullPrompt(request, modelId) {
        const parts = [];
        parts.push(`Traduzir do idioma ${request.sourceLanguage} para ${request.targetLanguage}`);
        if (request.context) {
            parts.push(`Contexto: ${request.context}`);
        }
        parts.push(`Texto a traduzir:`);
        parts.push(request.prompt);
        if (request.preserveTechnicalTerms) {
            parts.push("\nIMPORTANTE: Preservar termos técnicos, siglas e nomes próprios.");
        }
        return parts.join("\n");
    }
    estimateCapabilities(modelName) {
        const lower = modelName.toLowerCase();
        if (lower.includes("llama3"))
            return ["temperature", "top_p"];
        if (lower.includes("mixtral"))
            return ["temperature", "top_p", "repeat_penalty"];
        return ["temperature"];
    }
}
