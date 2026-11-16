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
    | 'paragraph'
    | 'heading'
    | 'caption'
    | 'header'
    | 'footer'
    | 'table'
    | 'footnote'
    | 'other';
}

export interface AIProvider {
  id: string;
  name: string;
  type: 'commercial' | 'local';
}

export interface TranslationJob {
  id: string;
  sourcePath: string;
  outputPath?: string;
  sourceLanguage: string;
  targetLanguage: string;
  providerId?: string;
  modelId?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
}