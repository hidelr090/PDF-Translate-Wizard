import { PDFTextBlock } from "../../pdf/domain/interfaces/pdf-extractor";
import { PDFPage } from "../../pdf/domain/entities/pdf-document";

export enum ReconstructStrategy {
  A = "A", // Substituição de texto no documento original
  B = "B", // Reconstrução de blocos com coordenadas e estilos
  C = "C", // Reconstrução de página para layouts complexos
}

export interface ReconstructOptions {
  strategy: ReconstructStrategy;
  respectTechnicalTerms: boolean;
  preserveFormatting: boolean;
  allowPageExpansion: boolean;
  maxBlockHeightIncrease: number; // Altura máxima em% antes de expandir página
  fontFallback: string; // Fonte fallback para caracteres não suportados
  embedFonts: boolean;
}

export interface ReconstructedPage {
  pageNumber: number;
  originalDimensions: { width: number; height: number };
  newDimensions: { width: number; height: number };
  strategyUsed: ReconstructStrategy;
  blocks: ReconstructedBlock[];
  images: { id: string; data: Uint8Array; width: number; height: number }[];
  warnings: string[];
}

export interface ReconstructedBlock {
  id: string;
  originalType: "paragraph" | "heading" | "caption" | "header" | "footer" | "table" | "other";
  originalText: string;
  translatedText: string;
  boundingBox: { x0: number; y0: number; x1: number; y1: number };
  font: { family: string; size: number; color: number; bold: boolean; italic: boolean };
  strategy: ReconstructStrategy;
  warnings: string[];
}

export interface PDFReconstructor {
  reconstruct(
    documentInfo: PDFPage[],
    blocks: { originalText: string; translatedText: string; boundingBox: any; font: any; pageNumber: number }[],
    options: ReconstructOptions
  ): Promise<{ pages: ReconstructedPage[]; totalWarnings: number }>;
}