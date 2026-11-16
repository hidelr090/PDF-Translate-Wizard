import { ipcMain } from "electron";
import { PythonPDFExtractor } from "../../../src/modules/pdf/infrastructure/python-pdf-extractor";

let pdfExtractor: PythonPDFExtractor | null = null;

export function setupPDFIPC(): void {
  if (!pdfExtractor) {
    pdfExtractor = new PythonPDFExtractor();
  }

  ipcMain.handle("pdf:extract", async (_event, filePath: string) => {
    try {
      const result = await pdfExtractor!.extract(filePath);
      return { success: true, data: result };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  });

  ipcMain.handle("pdf:classify", async (_event, filePath: string) => {
    try {
      const result = await pdfExtractor!.classify(filePath);
      return { success: true, data: result };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  });

  ipcMain.handle("pdf:ocr", async (_event, payload: { filePath: string; pageNumber?: number; language?: string }) => {
    try {
      const result = await pdfExtractor!.ocr(payload.filePath, payload.pageNumber, payload.language);
      return { success: true, data: result };
    } catch (err: any) {
      return { success: false, error: err.message };
    }
  });

  console.log("[IPC] Handlers de PDF registrados");
}

export function getPDFIPC(): PythonPDFExtractor | null {
  return pdfExtractor;
}