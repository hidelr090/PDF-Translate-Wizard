export class PDFDocument {
    filePath;
    pages;
    metadata;
    totalPages;
    constructor(filePath, pages, metadata, totalPages) {
        this.filePath = filePath;
        this.pages = pages;
        this.metadata = metadata;
        this.totalPages = totalPages;
    }
    getPage(pageNumber) {
        return this.pages.find((p) => p.pageNumber === pageNumber);
    }
    getAllTextBlocks() {
        return this.pages.flatMap((p) => p.textBlocks);
    }
    getTextBlocksByPage(pageNumber) {
        const page = this.getPage(pageNumber);
        return page ? page.textBlocks : [];
    }
}
