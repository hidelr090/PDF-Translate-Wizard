export interface PDFTextBlock {
  id: string;
  pageNumber: number;
  text: string;
  boundingBox: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
  font?: {
    family?: string;
    size?: number;
    bold?: boolean;
    italic?: boolean;
  };
  alignment?: string;
  readingOrder: number;
  type:
    | "paragraph"
    | "heading"
    | "caption"
    | "header"
    | "footer"
    | "table"
    | "footnote"
    | "other";
}

export interface PDFTable {
  id: string;
  pageNumber: number;
  data: string[][];
  boundingBox: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
}

export interface PDFImage {
  id: string;
  pageNumber: number;
  boundingBox: {
    x0: number;
    y0: number;
    x1: number;
    y1: number;
  };
}

export interface PDFPage {
  pageNumber: number;
  width: number;
  height: number;
  orientation: "portrait" | "landscape";
  textBlocks: PDFTextBlock[];
  tables: PDFTable[];
  images: PDFImage[];
  hasExtractableText: boolean;
}

export interface PDFDocumentInfo {
  filePath: string;
  pages: PDFPage[];
  metadata: {
    title?: string;
    author?: string;
    subject?: string;
    creator?: string;
    producer?: string;
  };
  totalPages: number;
}

export interface DocumentClassification {
  documentType: "textual" | "tables" | "multi_column" | "image_heavy" | "scanned";
  characteristics: string[];
  recommendedStrategy: "A" | "B" | "C";
  needsOCR: boolean;
  complexity: "low" | "medium" | "high";
  totalPages: number;
  totalTextBlocks: number;
  totalTables: number;
  totalImages: number;
  multiColumnPages: number;
}

export interface PDFExtractor {
  extract(filePath: string): Promise<PDFDocumentInfo>;
  classify(filePath: string): Promise<DocumentClassification>;
  ocr(filePath: string, pageNumber?: number, language?: string): Promise<any>;
}