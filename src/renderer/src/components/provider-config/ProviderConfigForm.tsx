import React, { useState } from "react";
import { ipcClient } from "../../services/ipc-client";

interface ProviderConfigFormProps {
  onSave: (config: {
    providerId: string;
    name: string;
    type: "commercial" | "local";
    apiKey?: string;
    baseUrl?: string;
  }) => void;
  onCancel: () => void;
  initialConfig?: {
    providerId: string;
    name: string;
    type: "commercial" | "local";
    apiKey?: string;
    baseUrl?: string;
  };
}

export default function ProviderConfigForm({
  onSave,
  onCancel,
  initialConfig,
}: ProviderConfigFormProps) {
  const [form, setForm] = useState({
    providerId: initialConfig?.providerId || "openai",
    name: initialConfig?.name || "OpenAI",
    type: initialConfig?.type || "commercial",
    apiKey: initialConfig?.apiKey || "",
    baseUrl: initialConfig?.baseUrl || "",
  });

  const [status, setStatus] = useState<"idle" | "checking" | "success" | "error">("idle");
  const [statusMessage, setStatusMessage] = useState("");

  const testConnection = async () => {
    setStatus("checking");
    setStatusMessage("Testando conexão...");

    try {
      const result = await ipcClient.validateConnection(form.providerId);
      if (result) {
        setStatus("success");
        setStatusMessage("Conexão bem-sucedida!");
      } else {
        setStatus("error");
        setStatusMessage("Não foi possível conectar ao provedor.");
      }
    } catch (err: any) {
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
    if (status === "idle") return null;
    const isSuccess = status === "success";
    const bgClass = isSuccess ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
    const borderClass = isSuccess ? "border-green-200" : "border-red-200";
    return (
      <div className={`mt-3 p-2 rounded-lg ${borderClass}`}>
        <p className="text-sm">{statusMessage}</p>
      </div>
    );
  };

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm max-w-lg">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        {initialConfig ? "Editar Provedor" : "Adicionar Provedor"}
      </h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nome
          </label>
          <input
            value={form.name}
            onChange={(e) =>
              setForm((n) => ({ ...n, name: e.target.value as string }))
            }
            className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo
          </label>
          <select
            value={form.type}
            onChange={(e) =>
              setForm((n) => ({ ...n, type: e.target.value as "commercial" | "local" }))
            }
            className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="commercial">Comercial (OpenAI, Anthropic, Gemini)</option>
            <option value="local">Local (Ollama)</option>
          </select>
        </div>

        {form.type === "commercial" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              API Key
            </label>
            <input
              value={form.apiKey}
              onChange={(e) =>
                setForm((n) => ({ ...n, apiKey: e.target.value as string }))
              }
              type="password"
              className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="sk-..."
            />
          </div>
        )}

        {form.type === "local" && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              URL do Servidor Ollama
            </label>
            <input
              value={form.baseUrl}
              onChange={(e) =>
                setForm((n) => ({ ...n, baseUrl: e.target.value }))
              }
              type="text"
              className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="http://localhost:11434"
            />
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={testConnection}
            disabled={status !== "idle"}
            className="flex-1 py-2 border border-primary text-primary rounded-lg hover:bg-primary/10 transition-colors font-medium"
          >
            {status === "idle" ? "Testar Conexão" : "Testando..."}
          </button>
          <button onClick={onCancel} className="py-2 border-gray-300 rounded-lg hover:bg-gray-100 transition-colors font-medium">
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={status !== "idle"}
            className="py-2 border-green-500 text-green-500 rounded-lg hover:bg-green-100 transition-colors font-medium"
          >
            Salvar
          </button>
        </div>
      </div>

      {this.renderStatusBadge()}
    </section>
  );
}
