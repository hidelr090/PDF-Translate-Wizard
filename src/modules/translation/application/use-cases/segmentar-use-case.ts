import { SegmentadorConfig, TranslationBlock, GlossaryTerm } from "../../domain/interfaces/translation-engine";

export class SegmentadorUseCase {
  private config: SegmentadorConfig;

  constructor(config: SegmentadorConfig = {}) {
    this.config = config;
  }

  async segmentar(
    blocks: TranslationBlock[],
    glossaryTerms: GlossaryTerm[]
  ): Promise<TranslationBlock[]> {
    const segmented: TranslationBlock[] = [];
    const { respectColumnBreaks = true, preserveParagraphs = true,
            maxTokensPerSegment = 2000, includeContext = true, contextLines = 1 } = this.config;

    let currentSegment: TranslationBlock | null = null;
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
      } else {
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

  private deveNovoSegmento(
    block: TranslationBlock,
    current: TranslationBlock,
    respectColumnBreaks: boolean
  ): boolean {
    if (!respectColumnBreaks) return false;
    const currentRight = current.boundingBox?.x1 || 0;
    const blockLeft = block.boundingBox?.x0 || 0;
    return blockLeft > currentRight * 1.1;
  }

  private excedeuLimiteTokens(block: TranslationBlock, maxTokens: number): boolean {
    const estimatedTokens = block.originalText.split(/\s+/).length;
    return estimatedTokens > maxTokens;
  }

  private aplicarGlossario(
    blocks: TranslationBlock[],
    glossaryTerms: GlossaryTerm[]
  ): TranslationBlock[] {
    if (!glossaryTerms || glossaryTerms.length === 0) return blocks;

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

  private escapeRegex(string: string): string {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }
}
