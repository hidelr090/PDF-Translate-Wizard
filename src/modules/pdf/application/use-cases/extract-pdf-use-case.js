export class ExtractPDFUseCase {
    pdfExtractor;
    constructor(pdfExtractor) {
        this.pdfExtractor = pdfExtractor;
    }
    async execute(filePath) {
        return this.pdfExtractor.extract(filePath);
    }
    async classify(filePath) {
        return this.pdfExtractor.classify(filePath);
    }
    async performOCR(filePath, pageNumber, language) {
        return this.pdfExtractor.ocr(filePath, pageNumber, language);
    }
}
