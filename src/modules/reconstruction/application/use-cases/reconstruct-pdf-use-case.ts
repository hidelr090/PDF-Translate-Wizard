import { PDFReconstructor, ReconstructOptions, ReconstructedPage, ReconstructedBlock, ReconstructStrategy } from "../../domain/interfaces/pdf-reconstructor";
import { pdfLib } from "pdf-lib";
import { createCanvas, loadImage } from "canvas";

export class ReconstructPDFUseCase implements PDFReconstructor {
  private fontsDir: string;

  constructor(fontsDir?: string) {
    this.fontsDir = fontsDir || "./fonts";
  }

  async reconstruct(
    documentInfo: any[],
    blocks: any[],
    options: ReconstructOptions
  ): Promise<{ pages: ReconstructedPage[]; totalWarnings: number }> {
    const { strategy, respectTechnicalTerms, preserveFormatting, allowPageExpansion = true, maxBlockHeightIncrease = 50, fontFallback = "DejaVuSans", embedFonts = true } = options;

    const totalWarnings: string[] = [];
    const reconstructedPages: ReconstructedPage[] = [];

    // Agrupar blocos por página
    const blocksByPage = this.agruparPorPagina(blocks);

    for (const [pageNumber, pageBlocks] of Object.entries(blocksByPage)) {
      const pageNum = parseInt(pageNumber, 10);

      // Encontrar página original
      const paginaOriginal = documentInfo.find((p: any) => p.pageNumber === pageNum);
      if (!paginaOriginal) continue;

      let estrategia: ReconstructStrategy = strategy;
      if (strategy === ReconstructStrategy.A) {
        estrategia = this.escolherEstrategiaA(paginaOriginal, pageBlocks, respectTechnicalTerms);
      } else if (strategy === ReconstructStrategy.B) {
        estrategia = ReconstructStrategy.B;
      } else if (strategy === ReconstructStrategy.C) {
        estrategia = ReconstructStrategy.C;
      }

      try {
        const resultado = await this.executarEstrategia(estrategia, paginaOriginal, pageBlocks, {
          respectTechnicalTerms,
          preserveFormatting,
          allowPageExpansion,
          maxBlockHeightIncrease,
          fontFallback,
          embedFonts,
        });

        reconstructedPages.push({
          pageNumber: pageNum,
          originalDimensions: { width: paginaOriginal.width, height: paginaOriginal.height },
          newDimensions: { width: paginaOriginal.width, height: resultado.newHeight },
          strategyUsed: estrategia,
          blocks: resultado.blocks,
          images: resultado.images,
          warnings: resultado.warnings,
        });

        totalWarnings.push(...resultado.warnings);
      } catch (err) {
        totalWarnings.push(`Erro ao processar página ${pageNum}: ${err instanceof Error ? err.message : "Erro desconhecido"}`);
      }
    }

    return { pages: reconstructedPages, totalWarnings: totalWarnings.length };
  }

  private agruparPorPagina(blocks: any[]): Map<number, any[]> {
    const byPage = new Map<number, any[]>();
    for (const block of blocks) {
      const page = block.pageNumber;
      if (!byPage.has(page)) byPage.set(page, []);
      byPage.get(page)!.push(block);
    }
    return byPage;
  }

  private escolherEstrategiaA(paginaOriginal: any, blocos: any[], respectTechnicalTerms: boolean): ReconstructStrategy {
    // Estratégia A: Substituição de texto no documento original
    // Verifica se a tradução caberia nas mesmas coordenadas
    const totalExpansao = blocos.reduce((sum: number, b: any) => {
      const originalHeight = b.boundingBox?.y1 - b.boundingBox?.y0 || 0;
      const traduzidoHeight = (b.translatedText.length / b.originalText.length) * originalHeight;
      return sum + Math.max(0, traduzidoHeight - originalHeight);
    }, 0);

    // Se a expansão for menor que 50%, usa-se a estratégia A
    if (totalExpansao / (paginaOriginal.height || 1) < maxBlockHeightIncrease / 100) {
      return ReconstructStrategy.A;
    }
    return ReconstructStrategy.C; // Muda para C se precisar expandir muito
  }

  private async executarEstrategiaA(
    paginaOriginal: any,
    blocos: any[],
    options: { respectTechnicalTerms: boolean; preserveFormatting: boolean; allowPageExpansion: boolean; maxBlockHeightIncrease: number; fontFallback: string; embedFonts: boolean }
  ): Promise<{ blocks: ReconstructedBlock[]; newHeight: number; images: any[]; warnings: string[] }> {
    const warnings: string[] = [];
    const reconstructedBlocks: ReconstructedBlock[] = [];
    let newHeight = paginaOriginal.height;

    for (const bloco of blocos) {
      const { originalText, translatedText, boundingBox, font } = bloco;
      
      // Calcula a nova altura baseada na razão de expansão do texto
      const razaoExpansao = translatedText.length / Math.max(1, originalText.length);
      const novaAltura = Math.max(boundingBox.y1 - boundingBox.y0, (boundingBox.y1 - boundingBox.y0) * razaoExpansao);

      // Verifica se cabe na altura original
      if (novaAltura <= (paginaOriginal.height || 1)) {
        // Substitui o texto mantendo as mesmas coordenadas
        reconstructedBlocks.push({
          id: bloco.id || `recon_${Math.random().toString(36).substr(2, 9)}`,
          originalType: bloco.type || "paragraph",
          originalText,
          translatedText,
          boundingBox: {
            x0: boundingBox.x0,
            y0: boundingBox.y0,
            x1: boundingBox.x1,
            y1: boundingBox.y0 + novaAltura,
          },
          font: this.mapearFont(font, bloco),
          strategy: ReconstructStrategy.A,
          warnings: [],
        });
      } else {
        // Expande a página se permitido
        if (options.allowPageExpansion) {
          const novaPaginaHeight = paginaOriginal.height + (novaAltura - (paginaOriginal.height || 1));
          newHeight = Math.max(newHeight, novaPaginaHeight);

          reconstructedBlocks.push({
            id: bloco.id || `recon_${Math.random().toString(36).substr(2, 9)}`,
            originalType: bloco.type || "paragraph",
            originalText,
            translatedText,
            boundingBox: {
              x0: boundingBox.x0,
              y0: boundingBox.y0,
              x1: boundingBox.x1,
              y1: novaPaginaHeight,
            },
            font: this.mapearFont(font, bloco),
            strategy: ReconstructStrategy.A,
            warnings: [`Texto expandido da página ${paginaOriginal.pageNumber}`],
          });
        } else {
          // Mantém altura original, corrige o texto cortado
          reconstructedBlocks.push({
            id: bloco.id || `recon_${Math.random().toString(36).substr(2, 9)}`,
            originalType: bloco.type || "paragraph",
            originalText,
            translatedText: translatedText.substring(0, Math.round(translatedText.length * (paginaOriginal.height || 1) / novaAltura)) + "...",
            boundingBox: {
              x0: boundingBox.x0,
              y0: boundingBox.y0,
              x1: boundingBox.x1,
              y1: paginaOriginal.height,
            },
            font: this.mapearFont(font, bloco),
            strategy: ReconstructStrategy.A,
            warnings: [`Texto cortado na página ${paginaOriginal.pageNumber}`],
          });
        }
      }
    }

    return { blocks: reconstructedBlocks, newHeight, images: [], warnings };
  }

  private mapearFont(font: any, bloco: any): { family: string; size: number; color: number; bold: boolean; italic: boolean } {
    return {
      family: font?.family || "DejaVuSans",
      size: font?.size || 12,
      color: font?.color || 0,
      bold: font?.bold || false,
      italic: font?.italic || false,
    };
  }

  private async executarEstrategiaB(
    paginaOriginal: any,
    blocos: any[],
    options: any
  ): Promise<{ blocks: ReconstructedBlock[]; newHeight: number; images: any[]; warnings: string[] }> {
    // Estratégia B: Reconstrução de blocos com coordenadas e estilos
    // Usa as coordenadas originais e redesenha o texto com o novo conteúdo
    const warnings: string[] = [];
    const reconstructedBlocks: ReconstructedBlock[] = [];
    let newHeight = paginaOriginal.height;

    for (const bloco of blocos) {
      const { originalText, translatedText, boundingBox, font } = bloco;

      // Mantém as coordenadas originais, mas redimensiona a fonte se necessário
      const razaoExpansao = translatedText.length / Math.max(1, originalText.length);
      const novaAltura = razaoExpansao * (boundingBox.y1 - boundingBox.y0);

      let novaAlturaLimitada = novaAltura;
      if (novaAltura > (paginaOriginal.height || 1) * (1 + (options.maxBlockHeightIncrease || 50) / 100)) {
        novaAlturaLimitada = (paginaOriginal.height || 1) * (1 + (options.maxBlockHeightIncrease || 50) / 100);
        warnings.push(`Bloco expandido na página ${bloco.pageNumber}`);
      }

      // Se a fonte não suportar caracteres do idioma de destino, usa-se fallback
      const familiaFonte = this.verificarSuporteFontes(font.family, translatedText, options.fontFallback || "DejaVuSans");

      reconstructedBlocks.push({
        id: bloco.id || `recon_${Math.random().toString(36).substr(2, 9)}`,
        originalType: bloco.type || "paragraph",
        originalText,
        translatedText,
        boundingBox: {
          x0: boundingBox.x0,
          y0: boundingBox.y0,
          x1: boundingBox.x1,
          y1: boundingBox.y0 + novaAlturaLimitada,
        },
        font: {
          family: familiaFonte,
          size: font?.size || 12,
          color: font?.color || 0,
          bold: font?.bold || false,
          italic: font?.italic || false,
        },
        strategy: ReconstructStrategy.B,
        warnings: [],
      });

      if (novaAlturaLimitada > newHeight) {
        newHeight = novaAlturaLimitada;
      }
    }

    return { blocks: reconstructedBlocks, newHeight, images: [], warnings };
  }

  private verificarSuporteFontes(familia: string, texto: string, fallback: string): string {
    // Em um implementação real, verificaria se a fonte suporta os glifos necessários
    // Por agora, retorna o fallback se o texto contiver caracteres fora do ASCII básico
    const temCaracteresEspeciais = /[^\x00-\x7F]/.test(texto);
    return fallback;
  }

  private async executarEstrategiaC(
    paginaOriginal: any,
    blocos: any[],
    options: any
  ): Promise<{ blocks: ReconstructedBlock[]; newHeight: number; images: any[]; warnings: string[] }> {
    // Estratégia C: Reconstrução de página para layouts complexos
    // Renderiza a página como imagem de referência e reconstrui o texto em um novo layout
    const warnings: string[] = [];
    const reconstructedBlocks: ReconstructedBlock[] = [];
    let newHeight = paginaOriginal.height;

    // Para a estratégia C, criamos um novo layout baseado no conteúdo traduzido
    // Este é o caso mais complexo - páginas que não podem ser preservadas pelas estratégias A ou B

    // Agrupa blocos por linha e reorganiza
    const blocosOrdenados = blocos.sort((a: any, b: any) => {
      const aTop = a.boundingBox?.y0 || 0;
      const bTop = b.boundingBox?.y0 || 0;
      return aTop - bTop;
    });

    let alturaAtual = 0;
    let linhaAtualBlocks: any[] = [];

    for (const bloco of blocosOrdenados) {
      const razaoExpansao = bloco.translatedText.length / Math.max(1, bloco.originalText.length);
      const alturaBloco = (bloco.boundingBox?.y1 - bloco.boundingBox?.y0 || 12) * razaoExpansao;

      // Se esta linha não coube na altura restante
      if (alturaAtual + alturaBloco > (paginaOriginal.height || 1) * 0.95) {
        // Processa a linha atual
        const resultadoLinha = this.processarLinhaLinha(linhaAtualBlocks, paginaOriginal.width, options);
        reconstructedBlocks.push(...resultadoLinha.blocks);
        newHeight = Math.max(newHeight, resultadoLinha.alturaLinha + alturaAtual);
        alturaAtual = resultadoLinha.alturaLinha;
        linhaAtualBlocks = [];
      }

      linhaAtualBlocks.push(bloco);
    }

    // Processa a última linha
    if (linhaAtualBlocks.length > 0) {
      const resultadoLinha = this.processarLinhaLinha(linhaAtualBlocks, paginaOriginal.width, options);
      reconstructedBlocks.push(...resultadoLinha.blocks);
      newHeight = Math.max(newHeight, resultadoLinha.alturaLinha + alturaAtual);
    }

    // Se a página precisou ser expandida significativamente
    if (newHeight > paginaOriginal.height * 1.3 && options.allowPageExpansion) {
      newHeight = paginaOriginal.height * 1.3; // Expande em no máximo 30%
      warnings.push(`Página ${paginaOriginal.pageNumber} expandida para acomodar tradução`);
    }

    return { blocks: reconstructedBlocks, newHeight, images: [], warnings };
  }

  private processarLinhaLinha(blocosLinha: any[], larguraPagina: number, options: any): { blocks: ReconstructedBlock[]; alturaLinha: number } {
    const reconstructedBlocks: ReconstructedBlock[] = [];
    let alturaLinha = 0;

    for (const bloco of blocosLinha) {
      const razaoExpansao = bloco.translatedText.length / Math.max(1, bloco.originalText.length);
      const novaAltura = (bloco.boundingBox?.y1 - bloco.boundingBox?.y0 || 12) * razaoExpansao;

      reconstructedBlocks.push({
        id: bloco.id || `recon_${Math.random().toString(36).substr(2, 9)}`,
        originalType: bloco.type || "paragraph",
        originalText: bloco.originalText,
        translatedText: bloco.translatedText,
        boundingBox: {
          x0: bloco.boundingBox?.x0 || 0,
          y0: alturaLinha,
          x1: bloco.boundingBox?.x1 || larguraPagina,
          y1: alturaLinha + novaAltura,
        },
        font: this.mapearFont(bloco.font, bloco),
        strategy: ReconstructStrategy.C,
        warnings: [],
      });

      alturaLinha += novaAltura;
    }

    return { blocks: reconstructedBlocks, alturaLinha };
  }

  private verificarSuporteFontesAvançado(familia: string, texto: string, fallback: string): string {
    // Versão avançada que tentaria carregar a fonte e verificar glifos
    // Por agora, usa a mesma lógica simplificada
    return /[^\x00-\x7F]/.test(texto) ? fallback : familia;
  }
}
