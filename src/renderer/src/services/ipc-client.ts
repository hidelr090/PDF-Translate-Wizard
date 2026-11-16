export interface PDFDocumentInfo {
  filePath: string;
  pages: Array<{
    pageNumber: number;
    width: number;
    height: number;
    orientation: string;
    textBlocks: Array<{
      id: string;
      text: string;
      boundingBox: { x0: number; y0: number; x1: number; y1: number };
      font?: { family?: string; size?: number; bold?: boolean; italic?: boolean };
      readingOrder: number;
      type: string;
    }>;
    tables: Array<any>;
    images: Array<any>;
    hasExtractableText: boolean;
  }>;
  metadata: any;
  totalPages: number;
}

export interface DocumentClassification {
  documentType: string;
  characteristics: string[];
  recommendedStrategy: string;
  needsOCR: boolean;
  complexity: string;
  totalPages: number;
  totalTextBlocks: number;
  totalTables: number;
  totalImages: number;
}

class IPCClient {
  async ping(): Promise<string> {
    return (window as any).electronAPI?.ping();
  }

  async extractPDF(filePath: string): Promise<PDFDocumentInfo> {
    const result = await (window as any).electronAPI?.pdfExtract(filePath);
    if (!result?.success) {
      throw new Error(result?.error || "Erro ao extrair PDF");
    }
    return result.data;
  }

  async classifyDocument(filePath: string): Promise<DocumentClassification> {
    const result = await (window as any).electronAPI?.pdfClassify(filePath);
    if (!result?.success) {
      throw new Error(result?.error || "Erro ao classificar documento");
    }
    return result.data;
  }

  async performOCR(payload: {
    filePath: string;
    pageNumber?: number;
    language?: string;
  }): Promise<any> {
    const result = await (window as any).electronAPI?.pdfOCR(payload);
    if (!result?.success) {
      throw new Error(result?.error || "Erro no OCR");
    }
    return result.data;
  }
}

export const ipcClient = new IPCClient();