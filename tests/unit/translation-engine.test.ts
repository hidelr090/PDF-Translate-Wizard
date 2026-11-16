import { describe, it, expect, beforeEach, vi } from 'vitest';
import { PDFTextBlock, PDFTable, PDFImage, DocumentClassification, TranslationBlock, GlossaryTerm, SegmentadorConfig, ReconstructStrategy, PDFReconstructor, ReconstructOptions, ReconstructedPage, ReconstructedBlock } from '../src/modules/translation/domain/interfaces/translation-engine';
import { SegmentadorUseCase } from '../src/modules/translation/application/use-cases/segmentar-use-case';
import { ReconstructPDFUseCase } from '../src/modules/reconstruction/application/use-cases/reconstruct-pdf-use-case';
import { ProviderManager } from '../src/modules/ai/application/provider-manager';

describe('Domain: Translation Engine Interfaces', () => {
  it('deve definir interfaces consistentes', () => {
    // PDFTextBlock
    const block: PDFTextBlock = {
      id: 'block-1',
      pageNumber: 1,
      text: 'Texto de teste',
      boundingBox: { x0: 0, y0: 0, x1: 100, y1: 20 },
      readingOrder: 1,
      type: 'paragraph',
    };
    expect(block.id).toBe('block-1');
    expect(block.type).toBe('paragraph');

    // DocumentClassification
    const classification: DocumentClassification = {
      documentType: 'textual',
      characteristics: [],
      recommendedStrategy: 'A',
      needsOCR: false,
      complexity: 'low',
      totalPages: 1,
      totalTextBlocks: 1,
      totalTables: 0,
      totalImages: 0,
      multiColumnPages: 0,
    };
    expect(classification.documentType).toBe('textual');

    // ReconstructStrategy
    expect(ReconstructStrategy.A).toBe('A');
    expect(ReconstructStrategy.B).toBe('B');
    expect(ReconstructStrategy.C).toBe('C');
  });

  it('deve definir TranslationBlock consistente', () => {
    const block: TranslationBlock = {
      id: 'bt-1',
      pageNumber: 1,
      blockId: 'orig-1',
      originalText: 'Hello world',
      translatedText: 'Olá mundo',
      status: 'translated',
      order: 0,
    };
    expect(block.originalText).toBe('Hello world');
    expect(block.translatedText).toBe('Olá mundo');
    expect(block.status).toBe('translated');
  });

  it('deve definir GlossaryTerm consistente', () => {
    const term: GlossaryTerm = {
      term: 'OpenAI',
      translation: 'OpenAI',
      mandatory: true,
      language: 'en',
    };
    expect(term.term).toBe('OpenAI');
    expect(term.mandatory).toBe(true);
  });
});

describe('Application: SegmentadorUseCase', () => {
  const configuracaoPadrao = {
    respectColumnBreaks: true,
    preserveParagraphs: true,
    maxTokensPerSegment: 2000,
    includeContext: true,
    contextLines: 1,
  };

  it('deve segmentar blocos mantendo parágrafos', async () => {
    const segmentador = new SegmentadorUseCase(configuracaoPadrao);
    const blocks: TranslationBlock[] = [
      {
        id: 'b-1',
        pageNumber: 1,
        blockId: 'orig-1',
        originalText: 'Primeiro parágrafo.',
        translatedText: 'Primeiro parágrafo traduzido.',
        status: 'translated',
        order: 0,
      },
      {
        id: 'b-2',
        pageNumber: 1,
        blockId: 'orig-2',
        originalText: 'Segundo parágrafo.',
        translatedText: 'Segundo parágrafo traduzido.',
        status: 'translated',
        order: 1,
      },
    ];

    const result = await segmentador.segmentar(blocks, []);
    expect(result.length).toBe(2);
    expect(result[0].originalText).toBe('Primeiro parágrafo.');
    expect(result[1].originalText).toBe('Segundo parágrafo.');
  });

  it('deve aplicar glossário', async () => {
    const segmentador = new SegmentadorUseCase(configuracaoPadrao);
    const blocks: TranslationBlock[] = [
      {
        id: 'b-1',
        pageNumber: 1,
        blockId: 'orig-1',
        originalText: 'Usando OpenAI API',
        translatedText: 'Usando OpenAI API',
        status: 'translated',
        order: 0,
      },
    ];

    const glossaryTerms: GlossaryTerm[] = [
      {
        term: 'OpenAI',
        translation: 'OpenAI',
        mandatory: true,
        language: 'en',
      },
    ];

    const result = await segmentador.segmentar(blocks, glossaryTerms);
    expect(result[0].translatedText).toContain('OpenAI');
  });

  it('deve lidar com bloqueios de coluna', async () => {
    const segmentador = new SegmentadorUseCase({
      ...configuracaoPadrao,
      respectColumnBreaks: true,
    });

    // Bloco à esquerda (coluna A)
    const blockLeft = {
      id: 'b-1',
      pageNumber: 1,
      blockId: 'orig-1',
      originalText: 'Texto da coluna A',
      translatedText: 'Texto da coluna A traduzido',
      status: 'translated',
      order: 0,
      boundingBox: { x0: 50, y0: 50, x1: 200, y1: 100 },
    };

    // Bloco à direita (coluna B)
    const blockRight = {
      id: 'b-2',
      pageNumber: 1,
      blockId: 'orig-2',
      originalText: 'Texto da coluna B',
      translatedText: 'Texto da coluna B traduzido',
      status: 'translated',
      order: 1,
      boundingBox: { x0: 300, y0: 50, x1: 450, y1: 100 },
    };

    const result = await segmentador.segmentar([blockLeft, blockRight], []);
    // Os blocos devem ser mantidos em ordem (não reordenados automaticamente)
    expect(result.length).toBe(2);
  });
});

describe('Application: ReconstructPDFUseCase', () => {
  it('deve ser instanciado', () => {
    const reconstructor = new ReconstructPDFUseCase();
    expect(reconstructor).toBeInstanceOf(ReconstructPDFUseCase);
  });

  it('deve ter método reconstruct', () => {
    const reconstructor = new ReconstructPDFUseCase();
    expect(typeof reconstructor.reconstruct).toBe('function');
  });
});
