/// <reference types="vite/client" />

interface Window {
  electronAPI?: {
    ping: () => Promise<string>;
    pdfExtract: (filePath: string) => Promise<any>;
    pdfClassify: (filePath: string) => Promise<any>;
    pdfOCR: (payload: {
      filePath: string;
      pageNumber?: number;
      language?: string;
    }) => Promise<any>;
  };
}