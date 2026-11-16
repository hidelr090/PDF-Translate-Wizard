import { contextBridge, ipcRenderer } from "electron";

// API exposta ao Renderer. Somente canais explicitamente autorizados.
// Usamos @ts-ignore pois o tipo ContextBridge do @types/electron@1.6.12
// não inclui o método exposeInMainApi (disponível em versões mais recentes).
// @ts-ignore
contextBridge.exposeInMainApi("electronAPI", {
  ping: () => ipcRenderer.invoke("app:ping"),

  // PDF
  pdfExtract: (filePath: string) =>
    ipcRenderer.invoke("pdf:extract", filePath),
  pdfClassify: (filePath: string) =>
    ipcRenderer.invoke("pdf:classify", filePath),
  pdfOCR: (payload: {
    filePath: string;
    pageNumber?: number;
    language?: string;
  }) => ipcRenderer.invoke("pdf:ocr", payload),
});