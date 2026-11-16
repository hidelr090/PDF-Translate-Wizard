export class ProviderManager {
    providers = new Map();
    configs = new Map();
    constructor() {
        this.loadDefaultConfigs();
    }
    loadDefaultConfigs() {
        const defaultConfigs = [
            { id: "openai", name: "OpenAI", type: "commercial", isActive: true, createdAt: new Date().toISOString() },
            { id: "anthropic", name: "Anthropic Claude", type: "commercial", isActive: true, createdAt: new Date().toISOString() },
            { id: "gemini", name: "Google Gemini", type: "commercial", isActive: true, createdAt: new Date().toISOString() },
            { id: "ollama", name: "Ollama (Local)", type: "local", isActive: true, createdAt: new Date().toISOString() },
        ];
        for (const config of defaultConfigs) {
            this.configs.set(config.id, config);
        }
    }
    getConfig(providerId) {
        return this.configs.get(providerId);
    }
    setConfig(config) {
        this.configs.set(config.id, config);
    }
    async validateConnection(providerId) {
        const provider = this.providers.get(providerId);
        if (!provider)
            return false;
        return await provider.validateConnection();
    }
    async listModels(providerId) {
        const provider = this.providers.get(providerId);
        if (!provider)
            return [];
        return await provider.listModels();
    }
    async translate(providerId, request) {
        const provider = this.providers.get(providerId);
        if (!provider) {
            return {
                success: false,
                translatedText: "",
                error: {
                    message: "Provedor não configurado",
                    type: "provider_not_configured",
                },
            };
        }
        try {
            const response = await provider.translate(request);
            return response;
        }
        catch (error) {
            return {
                success: false,
                translatedText: "",
                error: {
                    message: error.message || "Erro desconhecido",
                    type: error.type || "translation_error",
                },
            };
        }
    }
    registerProvider(provider, config) {
        this.providers.set(config.id, provider);
        this.configs.set(config.id, config);
    }
    unregisterProvider(providerId) {
        this.providers.delete(providerId);
    }
    getActiveProviders() {
        return Array.from(this.configs.values()).filter((c) => c.isActive);
    }
    getAllProviders() {
        return Array.from(this.providers.values());
    }
}
