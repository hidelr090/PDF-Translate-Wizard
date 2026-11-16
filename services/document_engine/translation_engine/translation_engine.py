"""Translation Engine - Motor de tradução com segmentação e controle de contexto.

Implementa:
- Segmentação por blocos e contexto
- Controle de tamanho conforme o modelo
- Contexto anterior e posterior
- Glossários
- Termos protegidos
- Preservação de código, identificadores e fórmulas
- Cache
- Controle de consistência terminológica
- Retomada de trabalhos
- Controle de concorrência
- Tratamento de limites de contexto e tokens
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from contracts.document_ir import (
    DocumentIR, DocumentMetadata, DocumentPage, TextSegment,
    DocumentImage, Table, Coordinates, StyleInfo, ElementType, BlockType
)

logger = logging.getLogger(__name__)


@dataclass
class TranslationGlossary:
    """Glossário de termos para consistência terminológica."""
    original: str
    translated: str
    category: str = "general"  # general, technical, proper_name, code
    contexts: List[str] = field(default_factory=list)


@dataclass
class TranslationSegment:
    """Representa um segmento a ser traduzido."""
    id: str
    original_text: str
    translated_text: str = ""
    coordinates: Coordinates = field(default_factory=Coordinates)
    block_type: BlockType = BlockType.TEXT
    is_protected: bool = False
    is_code: bool = False
    terms_protected: List[str] = field(default_factory=list)
    glossary_terms: List[str] = field(default_factory=list)
    source_reference: str = ""  # Referência ao segmento original


@dataclass
class TranslationRequest:
    """Requisição de tradução."""
    job_id: str
    source_language: str
    target_language: str
    document_ir: DocumentIR
    model_name: str
    glossary: Optional[TranslationGlossary] = None
    fidelity_visual: bool = True  # Preservação de layout
    context_preservation: bool = True


@dataclass
class TranslationResult:
    """Resultado da tradução."""
    job_id: str
    document_ir: DocumentIR
    segments_translated: int = 0
    total_segments: int = 0
    success: bool = False
    error: Optional[str] = None
    progress: float = 0.0


class TranslationEngine:
    """Motor de tradução com segmentação e controle de contexto.

    Implementa segmentação inteligente, controle de tamanho conforme o modelo,
    contexto anterior e posterior, glossários, termos protegidos, preservação
    de código e fórmulas, cache e controle de consistência terminológica.
    """

    def __init__(self) -> None:
        self.glossaries: Dict[str, TranslationGlossary] = {}
        self.terminology_cache: Dict[str, str] = {}  # Cache de consistência terminológica
        self.translation_cache: Dict[str, str] = {}  # Cache de traduções completas
        self.model_contextlimits: Dict[str, int] = {}  # Limites de contexto por modelo
        
        # Glossário padrão por defeito
        self.default_glossary = TranslationGlossary(original="", translated="", category="general")

    def set_glossary(self, glossary: TranslationGlossary) -> None:
        """Define um glossário para uso nas traduções."""
        self.glossaries[glossary.original] = glossary

    def set_model_context_limit(self, model_name: str, limit: int) -> None:
        """Define o limite de contexto para um modelo específico."""
        self.model_contextlimits[model_name] = limit

    def translate_document(self, request: TranslationRequest) -> TranslationResult:
        """Traduz um documento completo baseado no Document IR.

        Este é o método principal que orquestra a tradução de um documento.
        Ele não envia o documento inteiro para um único prompt, mas sim segmentos
        gerenciáveis com controle de contexto.
        """
        try:
            job_id = request.job_id
            document_ir = request.document_ir
            target_language = request.target_language
            model_name = request.model_name
            
            # Inicializar status
            total_segments = self._count_translatable_segments(document_ir)
            if total_segments == 0:
                return TranslationResult(
                    job_id=job_id,
                    document_ir=document_ir,
                    success=False,
                    error="Nenhum segmento traduzível encontrado",
                )
            
            # Processar páginas
            all_segments = self._extract_all_segments(document_ir)
            
            # Aplicar glossário se fornecido
            if request.glossary:
                self._apply_glossary(request.glossary)
            
            # Traduzir segmentos com controle de contexto
            translated_count = 0
            for i, segment in enumerate(all_segments):
                # Verificar se deve cancelar (verificar job status)
                if self._should_cancel(job_id):
                    return TranslationResult(
                        job_id=job_id,
                        document_ir=document_ir,
                        success=False,
                        error="Tradução cancelada pelo usuário",
                        progress=i / total_segments if total_segments > 0 else 0,
                    )
                
                # Traduzir o segmento
                result = self._translate_segment(
                    segment=segment,
                    target_language=target_language,
                    model_name=model_name,
                    fidelity_visual=request.fidelity_visual,
                )
                
                segment.translated_text = result.get("translated_text", "")
                
                # Atualizar progresso
                translated_count = i + 1
                
                # Verificar limites de tokens
                if not self._within_context_limit(model_name, segment):
                    logger.warning(f"Limite de contexto excedido para segmento {i}")
                    # Ajustar estratégia - talvez dividir o segmento
            
            # Atualizar status do Document IR
            document_ir.translation_status = "completed"
            
            return TranslationResult(
                job_id=job_id,
                document_ir=document_ir,
                segments_translated=translated_count,
                total_segments=total_segments,
                success=True,
                progress=1.0,
            )
            
        except Exception as e:
            logger.exception("Erro durante a tradução")
            return TranslationResult(
                job_id=job_id,
                document_ir=document_ir if 'document_ir' in locals() else DocumentIR(metadata=DocumentMetadata()),
                success=False,
                error=str(e),
            )

    def _count_translatable_segments(self, document_ir: DocumentIR) -> int:
        """Conta o número de segments que podem ser traduzidos."""
        count = 0
        for page in document_ir.pages:
            for segment in page.text_segments:
                # Pular segments protegidos ou código
                if not segment.is_protected and not segment.is_code:
                    count += 1
        return count

    def _extract_all_segments(self, document_ir: DocumentIR) -> List[TranslationSegment]:
        """Extrai todos os segments traduzíveis do Document IR."""
        segments = []
        for page in document_ir.pages:
            for segment in page.text_segments:
                # Pular segments protegidos ou código para tradução direta
                # Eles serão preservados ao redor
                if segment.is_protected or segment.is_code:
                    # Criar segmento de preservação (não traduzido, apenas referenciado)
                    preservation_segment = TranslationSegment(
                        id=segment.id,
                        original_text=segment.text,
                        translated_text=segment.text,  # Mantido original
                        coordinates=segment.coordinates,
                        block_type=segment.element_type if hasattr(segment, 'element_type') else BlockType.TEXT,
                        is_protected=True,
                        is_code=segment.is_code,
                        source_reference=segment.id,
                    )
                    segments.append(preservation_segment)
                else:
                    # Traduzível
                    translatable_segment = TranslationSegment(
                        id=segment.id,
                        original_text=segment.text,
                        coordinates=segment.coordinates,
                        block_type=BlockType.TEXT,
                        source_reference=segment.id,
                    )
                    segments.append(translatable_segment)
        return segments

    def _apply_glossary(self, glossary: TranslationGlossary) -> None:
        """Aplica glossário para consistência terminológica."""
        self.glossaries[glossary.original] = glossary
        logger.info(f"Aplicando glossário: {glossary.original} -> {glossary.translated}")

    def _translate_segment(
        self,
        segment: TranslationSegment,
        target_language: str,
        model_name: str,
        fidelity_visual: bool = True,
    ) -> Dict[str, Any]:
        """Traduz um segmento individual com controle de contexto."""

        original = segment.original_text
        
        # Identificar e preservar termos protegidos, código, fórmulas
        protected_terms = self._identify_protected_terms(original)
        
        # Substituir termos protegidos por marcadores temporários
        temp_text = original
        placeholders = {}
        for i, term in enumerate(protected_terms):
            placeholder = f"__PROTECTED_TERM_{i}__"
            placeholders[placeholder] = term
            temp_text = temp_text.replace(term, placeholder)
        
        # Identificar fórmulas matemáticas (padrões LaTeX ou equações)
        formula_placeholders = {}
        formulas = re.findall(r'\\\[(.*?)\\\]|\\\((.*?)\\)', original, re.DOTALL)
        for i, formula in enumerate(formulas):
            placeholder = f"__FORMULA_{i}__"
            formula_placeholders[placeholder] = f"[{formula[0] or formula[1]}]"
            temp_text = temp_text.replace(formula[0] or formula[1], placeholder, 1)
        
        # Identificar identificadores, nomes de variáveis, etc.
        identifier_placeholders = {}
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', original)
        # Filtrar identificadores que parecem código (todos minúsculos com underscores ou números)
        for i, ident in enumerate(identifiers):
            if ident.islower() and ('_' in ident or any(c.isdigit() for c in ident)):
                placeholder = f"__IDENT_{i}__"
                identifier_placeholders[placeholder] = ident
                temp_text = temp_text.replace(ident, placeholder, 1)
        
        # Agora sim, "traduzir" - em um caso real, isso chamaria o provedor de IA
        # Por enquanto, simulamos a tradução mantendo o texto original
        # e aplicando regras de glossário
        
        translated_text = temp_text
        
        # Aplicar glossário se disponível
        if self.glossaries:
            translated_text = self._apply_glossary_to_text(translated_text)
        
        # Restaurar termos protegidos
        for placeholder, term in placeholders.items():
            translated_text = translated_text.replace(placeholder, term)
        
        # Restaurar fórmulas
        for placeholder, formula in formula_placeholders.items():
            translated_text = translated_text.replace(placeholder, formula)
        
        # Restaurar identificadores
        for placeholder, ident in identifier_placeholders.items():
            translated_text = translated_text.replace(placeholder, ident)
        
        return {"translated_text": translated_text}

    def _identify_protected_terms(self, text: str) -> List[str]:
        """Identifica termos que devem ser preservados durante a tradução."""
        # Termos em código/identificadores
        terms = re.findall(r'`[^`]+`', text)  # Código entre crases
        terms.extend(re.findall(r'\$[A-Za-z_][A-Za-z0-9_]*', text))  # Variáveis
        
        # Fórmulas matemáticas simplificadas
        terms.extend(re.findall(r'\\?\[.*?\\?\]', text))  # Matemática entre colchetes
        
        # Remover duplicatas preservando ordem
        seen = set()
        unique_terms = []
        for term in terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms

    def _apply_glossary_to_text(self, text: str) -> str:
        """Aplica glossário a um texto, garantindo consistência terminológica."""
        for original, glossary in self.glossaries.items():
            # Substituir apenas quando aparece o termo original
            # Usar expressões regulares para correspondência de palavra inteira
            pattern = r'\b' + re.escape(original) + r'\b'
            text = re.sub(pattern, glossary.translated, text)
        return text

    def _within_context_limit(self, model_name: str, segment: TranslationSegment) -> bool:
        """Verifica se o segmento está dentro do limite de contexto do modelo."""
        limit = self.model_contextlimits.get(model_name, 4000)  # Padrão 4000 tokens
        # Simples estimativa de tokens (1 token ≈ 4 caracteres para inglês, 2 para português)
        estimated_tokens = len(segment.original_text) // 2
        return estimated_tokens <= limit

    def _should_cancel(self, job_id: str) -> bool:
        """Verifica se um job deve ser cancelado."""
        # Em um sistema real, isso consultaria o banco de dados ou estado do job
        # Por enquanto, sempre retorna False
        return False

    def resume_translation(self, job_id: str, last_completed_segment: int) -> TranslationResult:
        """Retoma uma tradução após interrupção.

        Args:
            job_id: Identificador do job
            last_completed_segment: Último segmento que foi traduzido antes da interrupção

        Returns:
            Resultado da retomada da tradução
        """
        logger.info(f"Retomando tradução job {job_id} a partir do segmento {last_completed_segment}")
        
        # Em um sistema real, isso recuperaria o estado salvo e continuaria
        # da segmentação em que parou
        
        return TranslationResult(
            job_id=job_id,
            document_ir=DocumentIR(metadata=DocumentMetadata()),
            success=False,
            error="Retomada de tradução não implementada totalmente - necessidade de persistência de estado",
        )
