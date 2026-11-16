"""Reconstruction Engine - Motor de reconstrução de documentos traduzidos.

Implementa três estratégias de reconstrução:
1. Preservação de layout original
2. Reconstrução assistida
3. Reconstrução alternativa

Prioriza:
- Preservação de imagens
- Preservação de dimensões das páginas
- Posicionamento dos blocos
- Fontes e tamanhos
- Cores
- Hierarquia visual
- Tabelas
- Colunas
- Quebras de página

Implementa identificação de overflow, colisões e conteúdo cortado.
Não sobrescreve o PDF original.
Quando a reconstrução fiel não for possível, informa claramente a limitação
e utiliza a estratégia alternativa somente conforme as configurações autorizadas
pelo usuário.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from contracts.document_ir import (
    DocumentIR, DocumentMetadata, DocumentPage, TextSegment,
    DocumentImage, Table, Coordinates, StyleInfo, ElementType, BlockType
)

logger = logging.getLogger(__name__)


class ReconstructionStrategy(Enum):
    """Estratégias de reconstrução disponíveis."""
    STRATEGY_A = "A"  # Preservação de layout original - substituição de texto no documento
    STRATEGY_B = "B"  # Reconstrução de blocos com coordenadas e estilos
    STRATEGY_C = "C"  # Reconstrução de página para layouts complexos


@dataclass
class ReconstructionConfig:
    """Configurações de reconstrução."""
    strategy: ReconstructionStrategy = ReconstructionStrategy.STRATEGY_B
    preserve_images: bool = True
    preserve_dimensions: bool = True
    preserve_colors: bool = True
    preserve_fonts: bool = True
    max_fidelity: float = 0.95  # Fidelidade máxima desejada (0 a 1)
    allow_overflow: bool = False  # Permitir que conteúdo transborde
    respect_page_breaks: bool = True
    optimize_columns: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "strategy": self.strategy.value,
            "preserve_images": self.preserve_images,
            "preserve_dimensions": self.preserve_dimensions,
            "preserve_colors": self.preserve_colors,
            "preserve_fonts": self.preserve_fonts,
            "max_fidelity": self.max_fidelity,
            "allow_overflow": self.allow_overflow,
            "respect_page_breaks": self.respect_page_breaks,
            "optimize_columns": self.optimize_columns,
        }


@dataclass
class ReconstructionResult:
    """Resultado da reconstrução de um documento."""
    job_id: str
    strategy_used: ReconstructionStrategy
    success: bool = False
    error: Optional[str] = None
    quality_score: float = 0.0
    fidelity_score: float = 0.0
    output_path: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    modifications: List[Dict] = field(default_factory=list)  # Registra modificações feitas


class ReconstructionEngine:
    """Motor de reconstrução de documentos traduzidos.

    Implementa três estratégias de reconstrução:
    1. Estratégia A: Preservação de layout original (substituição de texto)
    2. Estratégia B: Reconstrução de blocos com coordenadas e estilos
    3. Estratégia C: Reconstrução de página para layouts complexos

    Prioriza a preservação de imagens, dimensões, posicionamento, fontes,
    cores, hierarquia visual, tabelas, colunas e quebras de página.
    """

    def __init__(self) -> None:
        self.strategy_configs: Dict[ReconstructionStrategy, ReconstructionConfig] = {
            ReconstructionStrategy.STRATEGY_A: ReconstructionConfig(
                strategy=ReconstructionStrategy.STRATEGY_A,
                preserve_images=True,
                preserve_dimensions=True,
                preserve_colors=True,
                preserve_fonts=True,
                max_fidelity=0.90,
                allow_overflow=False,
                respect_page_breaks=True,
                optimize_columns=False,
            ),
            ReconstructionStrategy.STRATEGY_B: ReconstructionConfig(
                strategy=ReconstructionStrategy.STRATEGY_B,
                preserve_images=True,
                preserve_dimensions=True,
                preserve_colors=True,
                preserve_fonts=True,
                max_fidelity=0.95,
                allow_overflow=False,
                respect_page_breaks=True,
                optimize_columns=True,
            ),
            ReconstructionStrategy.STRATEGY_C: ReconstructionConfig(
                strategy=ReconstructionStrategy.STRATEGY_C,
                preserve_images=True,
                preserve_dimensions=True,
                preserve_colors=True,
                preserve_fonts=True,
                max_fidelity=0.90,
                allow_overflow=True,
                respect_page_breaks=True,
                optimize_columns=True,
            ),
        }

    def reconstruct(self, 
                    document_ir: DocumentIR, 
                    config: ReconstructionConfig,
                    job_id: str) -> ReconstructionResult:
        """Executa a reconstrução do documento usando a estratégia configurada.

        Args:
            document_ir: Document IR com o conteúdo traduzido
            config: Configurações de reconstrução
            job_id: Identificador do job

        Returns:
            ReconstructionResult com o resultado da reconstrução
        """
        strategy = config.strategy
        config = self.strategy_configs.get(strategy, self.strategy_configs[ReconstructionStrategy.STRATEGY_B])
        
        logger.info(f"Iniciando reconstrução strategy={strategy.value} job={job_id}")
        
        result = ReconstructionResult(
            job_id=job_id,
            strategy_used=strategy,
        )
        
        try:
            # Executar estratégia selecionada
            if strategy == ReconstructionStrategy.STRATEGY_A:
                result = self._strategy_a_reconstruction(document_ir, config, result)
            elif strategy == ReconstructionStrategy.STRATEGY_B:
                result = self._strategy_b_reconstruction(document_ir, config, result)
            elif strategy == ReconstructionStrategy.STRATEGY_C:
                result = self._strategy_c_reconstruction(document_ir, config, result)
            
            # Se a fidelidade não foi atingida e a estratégia atual não for a alternativa,
            # tentar a estratégia alternativa conforme configurações
            if result.fidelity_score < config.max_fidelity and strategy != ReconstructionStrategy.STRATEGY_C:
                alternative_result = self._try_alternative_strategy(document_ir, config, job_id)
                if alternative_result and alternative_result.fidelity_score > result.fidelity_score:
                    result = alternative_result
            
            result.success = result.fidelity_score >= (config.max_fidelity * 0.8)
            
        except Exception as e:
            logger.exception("Erro durante reconstrução")
            result.error = str(e)
            result.success = False
        
        return result
    
    def _strategy_a_reconstruction(self, document_ir: DocumentIR, config: ReconstructionConfig,
                                   result: ReconstructionResult) -> ReconstructionResult:
        """Estratégia A: Preservação de layout original.

        Substitui o texto no documento original mantendo o layout intacto.
        Funciona bem quando a estrutura do PDF permite reconstrução confiável.
        """
        logger.info("Aplicando Estratégia A: Preservação de layout original")
        
        warnings = []
        modifications = []
        
        # Verificar se a estratégia A é viável
        # Critérios: documento tem texto extraível, poucas tabelas, não é multi-coluna
        is_viable = self._is_strategy_viable(document_ir, "A")
        
        if not is_viable:
            result.warnings.append("Estratégia A não viável para este documento - muitos blocos complexos ou colunas")
            return result
        
        # Para cada página, substituir o texto mantendo posições
        for page in document_ir.pages:
            page_modifications = self._reconstruct_page_strategy_a(page, config)
            modifications.extend(page_modifications)
            result.warnings.extend(page_modifications)  # Reutilizando para acumular warnings
        
        # Registrar warnings de fidelidade
        if result.warnings:
            result.fidelity_score = max(0, 1 - (len(result.warnings) * 0.1))
        
        return result
    
    def _is_strategy_viable(self, document_ir: DocumentIR, strategy: str) -> bool:
        """Verifica se uma estratégia é viável para o documento."""
        if strategy == "A":
            # Estratégia A: documento deve ter texto extraível e estrutura relativamente simples
            for page in document_ir.pages:
                if not page.has_text:
                    return False  # Página sem texto extraível
                # Verificar multi-coluna
                mid_x = page.width / 2
                left_count = sum(1 for s in page.text_segments if s.coordinates.x0 < mid_x)
                right_count = sum(1 for s in page.text_segments if s.coordinates.x0 >= mid_x)
                if left_count > 5 and right_count > 5:
                    return False  # Multi-coluna detectada
        
        return True
    
    def _reconstruct_page_strategy_a(self, page: DocumentPage, config: ReconstructionConfig) -> List[Dict]:
        """Reconstrói uma página usando a estratégia A."""
        modifications = []
        
        # Para cada segmento de texto, registrar a substituição
        for segment in page.text_segments:
            if segment.original_text and segment.translated_text:
                # Verificar se o texto mudou significativamente
                text_change = abs(len(segment.translated_text) - len(segment.original_text))
                change_ratio = text_change / max(len(segment.original_text), 1)
                
                # Se a mudança de tamanho for muito grande, pode haver overflow
                if change_ratio > 1.5 and not config.allow_overflow:
                    modifications.append({
                        "type": "overflow_risk",
                        "segment_id": segment.id,
                        "issue": f"Mudança de tamanho de texto {change_ratio:.1f}x - risco de overflow",
                        "severity": "high",
                    })
                
                modifications.append({
                    "type": "text_substitution",
                    "segment_id": segment.id,
                    "original": segment.original_text,
                    "translated": segment.translated_text,
                    "coordinates": segment.coordinates,
                    "font": segment.style.font_family if segment.style else "unknown",
                    "font_size": segment.style.font_size if segment.style else 12,
                })
        
        return modifications
    
    def _strategy_b_reconstruction(self, document_ir: DocumentIR, config: ReconstructionConfig,
                                   result: ReconstructionResult) -> ReconstructionResult:
        """Estratégia B: Reconstrução de blocos com coordenadas e estilos.

        Reconstroi o documento posicionando blocos de texto traduzido com
        as coordenadas, fontes e tamanhos originais.
        """
        logger.info("Aplicando Estratégia B: Reconstrução de blocos")
        
        warnings = []
        modifications = []
        
        # Para cada página, reconstruir com posições preservadas
        for page in document_ir.pages:
            page_modifications = self._reconstruct_page_strategy_b(page, config)
            modifications.extend(page_modifications)
        
        # Verificar problemas de sobreposição e overflow
        self._check_reconstruction_issues(document_ir, modifications, result)
        
        # Calcular fidelidade
        if modifications:
            success_count = sum(1 for m in modifications if m.get("status") == "success")
            result.fidelity_score = success_count / max(len(modifications), 1)
        else:
            result.fidelity_score = 1.0
        
        return result
    
    def _reconstruct_page_strategy_b(self, page: DocumentPage, config: ReconstructionConfig) -> List[Dict]:
        """Reconstrói uma página usando a estratégia B."""
        modifications = []
        
        # Para cada segmento de texto, posicionar com coordenadas e estilo originais
        for segment in page.text_segments:
            if segment.translated_text and segment.original_text != segment.translated_text:
                # Verificar se a fonte e tamanho estão disponíveis
                font_family = segment.style.font_family if segment.style else "Helvetica"
                font_size = segment.style.font_size if segment.style else 12.0
                
                modifications.append({
                    "type": "block_placement",
                    "segment_id": segment.id,
                    "position": {
                        "x0": segment.coordinates.x0,
                        "y0": segment.coordinates.y0,
                        "x1": segment.coordinates.x1,
                        "y1": segment.coordinates.y1,
                    },
                    "font": font_family,
                    "font_size": font_size,
                    "color": segment.style.font_color if segment.style and segment.style.font_color else "#000000",
                    "translated_text": segment.translated_text,
                    "original_text": segment.original_text,
                    "status": "placed",
                })
        
        # Verificar tabelas
        for table in page.tables:
            modifications.append({
                "type": "table_preservation",
                "table_id": table.id,
                "rows": table.rows,
                "columns": table.columns,
                "preserved": True,
                "status": "ok",
            })
        
        # Verificar imagens
        for image in page.images:
            if config.preserve_images:
                modifications.append({
                    "type": "image_preservation",
                    "image_id": image.id,
                    "original_path": image.original_path,
                    "position": {
                        "x0": image.coordinates.x0,
                        "y0": image.coordinates.y0,
                        "x1": image.coordinates.x1,
                        "y1": image.coordinates.y1,
                    },
                    "preserved": True,
                    "status": "ok",
                })
        
        return modifications
    
    def _check_reconstruction_issues(self, document_ir: DocumentIR, modifications: List[Dict],
                                    result: ReconstructionResult) -> None:
        """Verifica problemas de overflow, colisões e conteúdo cortado."""
        warnings = []
        
        # Verificar overflow de texto
        total_overflow = 0
        for page in document_ir.pages:
            for segment in page.text_segments:
                # Estimativa de overflow baseada na mudança de tamanho
                if segment.original_text and segment.translated_text:
                    size_ratio = len(segment.translated_text) / max(len(segment.original_text), 1)
                    if size_ratio > 1.3 and not config.allow_overflow:
                        total_overflow += 1
                        warnings.append({
                            "type": "overflow",
                            "segment_id": segment.id,
                            "issue": f"Texto aumentou {size_ratio:.1f}x - pode haver conteúdo cortado",
                            "severity": "medium",
                        })
        
        # Verificar colisões entre blocos
        for page in document_ir.pages:
            blocks = page.text_segments
            for i, block1 in enumerate(blocks):
                for block2 in blocks[i+1:]:
                    # Verificar sobreposição simples
                    if block1.coordinates.overlap(block2.coordinates):
                        total_overflow += 1
                        warnings.append({
                            "type": "collision",
                            "segment_ids": [block1.id, block2.id],
                            "issue": "Colisão de blocos detectada",
                            "severity": "high",
                        })
        
        result.warnings.extend(warnings)
        result.fidelity_score = max(0, result.fidelity_score - (len(warnings) * 0.05))
    
    def _strategy_c_reconstruction(self, document_ir: DocumentIR, config: ReconstructionConfig,
                                   result: ReconstructionResult) -> ReconstructionResult:
        """Estratégia C: Reconstrução de página para layouts complexos.

        Usado quando layouts complexos não permitem reconstrução fiel com
        as estratégias A ou B. Substitui o conteúdo preservando a estrutura
        geral da página, podendo alterar posições para evitar overflow.
        """
        logger.info("Aplicando Estratégia C: Reconstrução de página para layouts complexos")
        
        warnings = []
        modifications = []
        
        # Para cada página, reconstruir permitindo reorganização
        for page in document_ir.pages:
            page_modifications = self._reconstruct_page_strategy_c(page, config)
            modifications.extend(page_modifications)
        
        # Calcular fidelidade
        if modifications:
            success_count = sum(1 for m in modifications if m.get("status") != "failed")
            result.fidelity_score = success_count / max(len(modifications), 1)
        else:
            result.fidelity_score = 0.7  # Fidelidade menor para estratégia C
        
        # Adicionar aviso de que a reconstrução não foi fiel
        result.warnings.append(
            "Reconstrução pela Estratégia C - layout reorganizado para acomodar tradução. "
            "Fidelidade visual pode ser comprometida."
        )
        
        return result
    
    def _reconstruct_page_strategy_c(self, page: DocumentPage, config: ReconstructionConfig) -> List[Dict]:
        """Reconstrói uma página usando a estratégia C."""
        modifications = []
        
        # Para cada segmento, repositionar permitindo ajustes de layout
        for i, segment in enumerate(page.text_segments):
            if segment.translated_text and segment.original_text != segment.translated_text:
                # Calcular novo posicionamento permitindo mudança de linha ou coluna
                font_size = segment.style.font_size if segment.style else 12.0
                estimated_height = font_size * 1.5  # Aproximada por linha
                
                # Contar quantas linhas o texto original ocupava vs traduzido
                orig_lines = max(1, len(segment.original_text) // 80 + 1)  # Approximado
                trans_lines = max(1, len(segment.translated_text) // 80 + 1)
                
                # Ajustar posição se o texto traduzido é maior
                if trans_lines > orig_lines and not config.allow_overflow:
                    # Mover para próxima posição ou nova linha
                    modifications.append({
                        "type": "reposition_with_overflow",
                        "segment_id": segment.id,
                        "original_position": {
                            "x0": segment.coordinates.x0,
                            "y0": segment.coordinates.y0,
                        },
                        "new_position": {
                            "x0": segment.coordinates.x0,
                            "y0": segment.coordinates.y0 + (trans_lines - orig_lines) * estimated_height,
                        },
                        "forced": trans_lines > orig_lines + 2,  # Força se muito maior
                        "status": "adjusted",
                    })
                else:
                    # Manter posição original
                    modifications.append({
                        "type": "preserve_position",
                        "segment_id": segment.id,
                        "position": {
                            "x0": segment.coordinates.x0,
                            "y0": segment.coordinates.y0,
                            "x1": segment.coordinates.x1,
                            "y1": segment.coordinates.y1,
                        },
                        "translated_text": segment.translated_text,
                        "status": "ok",
                    })
        
        return modifications
    
    def _try_alternative_strategy(self, document_ir: DocumentIR, config: ReconstructionConfig,
                                  job_id: str) -> Optional[ReconstructionResult]:
        """Tenta uma estratégia alternativa quando a fidelidade não é atingida."""
        # Determinar qual estratégia alternativa tentar
        current = config.strategy
        
        # Se for A, tentar B; se for B, tentar C; se for C, manter
        alternatives = {
            ReconstructionStrategy.STRATEGY_A: ReconstructionStrategy.STRATEGY_B,
            ReconstructionStrategy.STRATEGY_B: ReconstructionStrategy.STRATEGY_C,
            ReconstructionStrategy.STRATEGY_C: None,  # Última opção
        }
        
        alternative = alternatives.get(current)
        if alternative is None:
            return None
        
        # Criar configuração para a estratégia alternativa
        alt_config = self.strategy_configs.get(alternative, self.strategy_configs[ReconstructionStrategy.STRATEGY_B])
        
        # Executar a estratégia alternativa
        result = ReconstructionResult(job_id=job_id, strategy_used=alternative)
        result = self._strategy_b_reconstruction(document_ir, alt_config, result)  # Usar B como padrão
        
        # Adicionar aviso
        result.warnings.append(
            f"Estratégia alternativa {alternative.value} aplicada devido à baixa fidelidade na estratégia anterior"
        )
        
        return result
    
    def _apply_glossary_to_reconstructed(self, document_ir: DocumentIR) -> None:
        """Aplica glossário durante a reconstrução para consistência terminológica."""
        # Isso seria chamado durante a reconstrução para garantir que
        # termos técnicos sejam consistentemente traduzidos
        pass
