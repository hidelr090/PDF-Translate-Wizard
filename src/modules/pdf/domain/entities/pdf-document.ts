export class PDFDocument {
  constructor(
    public readonly filePath: string,
    public readonly pages: PDFPage[],
    public readonly metadata: PDFDocumentMetadata,
    public readonly totalPages: number
  ) {}

  getPage(pageNumber: number): PDFPage | undefined {
    return this.pages.find((p) => p.pageNumber === pageNumber);
  }

  getAllTextBlocks(): PDFTextBlock[] {
    return this.pages.flatMap((p) => p.textBlocks);
  }

  getTextBlocksByPage(pageNumber: number): PDFTextBlock[] {
    const page = this.getPage(pageNumber);
    return page ? page.textBlocks : [];
  }
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

export interface PDFDocumentMetadata {
  title?: string;
  author?: string;
  subject?: string;
  creator?: string;
  producer?: string;
}