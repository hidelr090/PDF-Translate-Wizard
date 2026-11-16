import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { ipcClient } from "../../services/ipc-client";
export default function ProviderConfigForm({ onSave, onCancel, initialConfig, }) {
    const [form, setForm] = useState({
        providerId: initialConfig?.providerId || "openai",
        name: initialConfig?.name || "OpenAI",
        type: initialConfig?.type || "commercial",
        apiKey: initialConfig?.apiKey || "",
        baseUrl: initialConfig?.baseUrl || "",
    });
    const [status, setStatus] = useState("idle");
    const [statusMessage, setStatusMessage] = useState("");
    const testConnection = async () => {
        setStatus("checking");
        setStatusMessage("Testando conexão...");
        try {
            const result = await ipcClient.validateConnection(form.providerId);
            if (result) {
                setStatus("success");
                setStatusMessage("Conexão bem-sucedida!");
            }
            else {
                setStatus("error");
                setStatusMessage("Não foi possível conectar ao provedor.");
            }
        }
        catch (err) {
            setStatus("error");
            setStatusMessage(`Erro: ${err.message}`);
        }
    };
    const handleSave = () => {
        onSave({
            providerId: form.providerId,
            name: form.name,
            type: form.type,
            apiKey: form.apiKey,
            baseUrl: form.baseUrl,
        });
        onCancel();
    };
    const renderStatusBadge = () => {
        if (status === "idle")
            return null;
        const isSuccess = status === "success";
        const bgClass = isSuccess ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
        const borderClass = isSuccess ? "border-green-200" : "border-red-200";
        return (_jsx("div", { className: `mt-3 p-2 rounded-lg ${borderClass}`, children: _jsx("p", { className: "text-sm", children: statusMessage }) }));
    };
    return (_jsxs("section", { className: "rounded-xl border border-gray-200 bg-white p-6 shadow-sm max-w-lg", children: [_jsx("h2", { className: "text-lg font-semibold text-gray-900 mb-4", children: initialConfig ? "Editar Provedor" : "Adicionar Provedor" }), _jsxs("div", { className: "space-y-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Nome" }), _jsx("input", { value: form.name, onChange: (e) => setForm((n) => ({ ...n, name: e.target.value })), className: "w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary", required: true })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Tipo" }), _jsxs("select", { value: form.type, onChange: (e) => setForm((n) => ({ ...n, type: e.target.value })), className: "w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary", children: [_jsx("option", { value: "commercial", children: "Comercial (OpenAI, Anthropic, Gemini)" }), _jsx("option", { value: "local", children: "Local (Ollama)" })] })] }), form.type === "commercial" && (_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "API Key" }), _jsx("input", { value: form.apiKey, onChange: (e) => setForm((n) => ({ ...n, apiKey: e.target.value })), type: "password", className: "w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "sk-..." })] })), form.type === "local" && (_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "URL do Servidor Ollama" }), _jsx("input", { value: form.baseUrl, onChange: (e) => setForm((n) => ({ ...n, baseUrl: e.target.value })), type: "text", className: "w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary", placeholder: "http://localhost:11434" })] })), _jsxs("div", { className: "flex gap-2", children: [_jsx("button", { onClick: testConnection, disabled: status !== "idle", className: "flex-1 py-2 border border-primary text-primary rounded-lg hover:bg-primary/10 transition-colors font-medium", children: status === "idle" ? "Testar Conexão" : "Testando..." }), _jsx("button", { onClick: onCancel, className: "py-2 border-gray-300 rounded-lg hover:bg-gray-100 transition-colors font-medium", children: "Cancelar" }), _jsx("button", { onClick: handleSave, disabled: status !== "idle", className: "py-2 border-green-500 text-green-500 rounded-lg hover:bg-green-100 transition-colors font-medium", children: "Salvar" })] })] }), this.renderStatusBadge()] }));
}
