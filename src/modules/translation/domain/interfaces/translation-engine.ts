export interface TranslationJob {
  id: string;
  sourceLanguage: string;
  targetLanguage: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  totalPages: number;
  processedPages: number;
  createdAt: Date;
  completedAt?: Date;
}

export interface TranslationBlock {
  id: string;
  pageNumber: number;
  blockId: string;
  originalText: string;
  translatedText: string;
  status: "pending" | "translating" | "translated" | "failed";
  order: number;
}

export interface SegmentadorConfig {
  respectColumnBreaks: boolean;
  preserveParagraphs: boolean;
  maxTokensPerSegment: number;
  includeContext: boolean;
  contextLines: number; // Número de linhas anteriores/posteriores para contexto
}

export interface GlossaryTerm {
  term: string;
  translation: string;
  mandatory: boolean;
  language: string;
}

export interface Glossary {
  id: string;
  name: string;
  terms: GlossaryTerm[];
  createdAt: Date;
}

export interface TranslationEngineConfig {
  respectTechnicalTerms: boolean;
  useGlossary: boolean;
  preserveFormatting: boolean;
  allowPageExpansion: boolean;
  maxConcurrentRequests: number;
  retryAttempts: number;
  retryDelay: number;
}