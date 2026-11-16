import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { useState, useCallback } from "react";
import { ipcClient } from "./services/ipc-client";
import PDFInfo from "./components/PDFInfo";
export default function App() {
    const [filePath, setFilePath] = useState(null);
    const [document, setDocument] = useState(null);
    const [classification, setClassification] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const handleSelectPDF = useCallback(async () => {
        // Em produção, isso abriria um dialog do Electron
        // Por enquanto, simulamos com um input de arquivo
        const input = document.createElement("input");
        input.type = "file";
        input.accept = ".pdf";
        input.onchange = async (e) => {
            const file = e.target.files?.[0];
            if (!file)
                return;
            setLoading(true);
            setError(null);
            setFilePath(file.path || file.name);
            try {
                const [docResult, classResult] = await Promise.all([
                    ipcClient.extractPDF(file.path || file.name),
                    ipcClient.classifyDocument(file.path || file.name),
                ]);
                setDocument(docResult);
                setClassification(classResult);
            }
            catch (err) {
                setError(err.message || "Erro ao processar PDF");
            }
            finally {
                setLoading(false);
            }
        };
        input.click();
    }, []);
    return (_jsxs("div", { className: "min-h-screen bg-gray-50", children: [_jsxs("header", { className: "border-b border-gray-200 bg-white px-6 py-4", children: [_jsx("h1", { className: "text-xl font-semibold text-gray-900", children: "PDF Translate Wizard" }), _jsx("p", { className: "text-sm text-gray-500", children: "Tradutor de PDF com preserva\u00E7\u00E3o de layout" })] }), _jsx("main", { className: "max-w-4xl mx-auto py-8 px-6", children: !filePath ? (_jsx("section", { className: "rounded-xl border-2 border-dashed border-gray-300 bg-white p-12 text-center shadow-sm hover:border-primary transition-colors", children: _jsxs("div", { className: "flex flex-col items-center justify-center", children: [_jsx("div", { className: "w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4", children: _jsx("svg", { className: "w-8 h-8 text-primary", fill: "none", stroke: "currentColor", viewBox: "0 0 24 24", children: _jsx("path", { strokeLinecap: "round", strokeLinejoin: "round", strokeWidth: 2, d: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" }) }) }), _jsx("h2", { className: "text-lg font-semibold text-gray-900 mb-2", children: "Selecione um PDF" }), _jsx("p", { className: "text-gray-600 mb-6", children: "Arraste um arquivo PDF ou clique para selecionar" }), _jsx("button", { onClick: handleSelectPDF, className: "px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors", children: "Escolher arquivo PDF" })] }) })) : (_jsxs(_Fragment, { children: [_jsxs("div", { className: "flex items-center justify-between mb-6", children: [_jsx("h2", { className: "text-lg font-semibold text-gray-900", children: "Documento carregado" }), _jsx("button", { onClick: () => {
                                        setFilePath(null);
                                        setDocument(null);
                                        setClassification(null);
                                        setError(null);
                                    }, className: "text-sm text-gray-500 hover:text-gray-700", children: "Escolher outro arquivo" })] }), _jsx(PDFInfo, { document: document, classification: classification, loading: loading, error: error })] })) })] }));
}
