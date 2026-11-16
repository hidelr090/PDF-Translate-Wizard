class IPCClient {
    async ping() {
        return window.electronAPI?.ping();
    }
    async extractPDF(filePath) {
        const result = await window.electronAPI?.pdfExtract(filePath);
        if (!result?.success) {
            throw new Error(result?.error || "Erro ao extrair PDF");
        }
        return result.data;
    }
    async classifyDocument(filePath) {
        const result = await window.electronAPI?.pdfClassify(filePath);
        if (!result?.success) {
            throw new Error(result?.error || "Erro ao classificar documento");
        }
        return result.data;
    }
    async performOCR(payload) {
        const result = await window.electronAPI?.pdfOCR(payload);
        if (!result?.success) {
            throw new Error(result?.error || "Erro no OCR");
        }
        return result.data;
    }
}
export const ipcClient = new IPCClient();
