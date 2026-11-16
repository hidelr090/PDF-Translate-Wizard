export class SegmentadorUseCase {
    config;
    constructor(config = {}) {
        this.config = config;
    }
    async segmentar(blocks, glossaryTerms) {
        const segmented = [];
        const { respectColumnBreaks = true, preserveParagraphs = true, maxTokensPerSegment = 2000, includeContext = true, contextLines = 1 } = this.config;
        let currentSegment = null;
        let currentOrder = 0;
        for (const block of blocks) {
            if (block.status !== "pending") {
                segmented.push(block);
                continue;
            }
            if (!currentSegment || this.deveNovoSegmento(block, currentSegment, respectColumnBreaks)) {
                if (currentSegment) {
                    currentSegment.order = currentOrder++;
                    segmented.push(currentSegment);
                }
                currentSegment = {
                    ...block,
                    id: block.id || `block_${block.pageNumber}_${block.order}`,
                    status: "translating",
                    order: 0,
                };
            }
            if (includeContext && currentSegment && contextLines > 0) {
                // Contexto seria implementado via ProviderManager
            }
            if (currentSegment && this.excedeuLimiteTokens(currentSegment, maxTokensPerSegment)) {
                currentSegment.order = currentOrder++;
                segmented.push(currentSegment);
                currentSegment = {
                    ...block,
                    id: block.id || `block_${block.pageNumber}_${block.order}`,
                    status: "translating",
                    order: 0,
                };
            }
            else {
                currentSegment.originalText += " " + block.originalText;
                if (block.boundingBox) {
                    currentSegment.boundingBox = {
                        x0: Math.min(currentSegment.boundingBox?.x0 || block.boundingBox.x0, block.boundingBox.x0),
                        y0: Math.min(currentSegment.boundingBox?.y0 || block.boundingBox.y0, block.boundingBox.y0),
                        x1: Math.max(currentSegment.boundingBox?.x1 || block.boundingBox.x1, block.boundingBox.x1),
                        y1: Math.max(currentSegment.boundingBox?.y1 || block.boundingBox.y1, block.boundingBox.y1),
                    };
                }
            }
        }
        if (currentSegment) {
            currentSegment.order = currentOrder++;
            segmented.push(currentSegment);
        }
        return this.aplicarGlossario(segmented, glossaryTerms);
    }
    deveNovoSegmento(block, current, respectColumnBreaks) {
        if (!respectColumnBreaks)
            return false;
        const currentRight = current.boundingBox?.x1 || 0;
        const blockLeft = block.boundingBox?.x0 || 0;
        return blockLeft > currentRight * 1.1;
    }
    excedeuLimiteTokens(block, maxTokens) {
        const estimatedTokens = block.originalText.split(/\s+/).length;
        return estimatedTokens > maxTokens;
    }
    aplicarGlossario(blocks, glossaryTerms) {
        if (!glossaryTerms || glossaryTerms.length === 0)
            return blocks;
        return blocks.map(block => {
            let translated = block.originalText;
            for (const term of glossaryTerms) {
                const regex = new RegExp(`\\b${this.escapeRegex(term.term)}\\b`, "gi");
                translated = translated.replace(regex, term.translation);
            }
            return {
                ...block,
                translatedText: translated,
            };
        });
    }
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }
}
