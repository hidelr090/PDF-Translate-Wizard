import { PDFExtractor, PDFDocumentInfo } from "../../domain/interfaces/pdf-extractor";
import { DocumentClassification } from "../../domain/interfaces/pdf-extractor";

export class ExtractPDFUseCase {
  constructor(private readonly pdfExtractor: PDFExtractor) {}

  async execute(filePath: string): Promise<PDFDocumentInfo> {
    return this.pdfExtractor.extract(filePath);
  }

  async classify(filePath: string): Promise<DocumentClassification> {
    return this.pdfExtractor.classify(filePath);
  }

  async performOCR(
    filePath: string,
    pageNumber?: number,
    language?: string
  ): Promise<any> {
    return this.pdfExtractor.ocr(filePath, pageNumber, language);
  }
}