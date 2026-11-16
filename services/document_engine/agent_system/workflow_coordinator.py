"""Workflow Coordinator - Coordenador determinístico que controla o fluxo de trabalho dos agentes.

O coordenador controla:
- Estado do trabalho
- Ordem das etapas
- Retry
- Limites de revisão
- Fallback
- Cancelamento
- Retomada
- Registro de execução

Não permite ciclos ilimitados de agentes.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

from contracts.document_ir import DocumentIR

logger = logging.getLogger(__name__)


@dataclass
class AgentExecution:
    """Registro da execução de um agente."""
    agent_name: str
    step: str
    status: str  # started, completed, failed, skipped
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    execution_time: float = 0.0
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class WorkflowState:
    """Estado atual do workflow."""
    job_id: str
    status: str = "initialized"  # initialized, running, paused, completed, failed, cancelled
    current_step: str = "start"
    steps_completed: int = 0
    total_steps: int = 0
    agent_executions: List[AgentExecution] = field(default_factory=list)
    cancellation_requested: bool = False
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowResult:
    """Resultado final do workflow."""
    job_id: str
    success: bool = False
    document_ir: Optional[DocumentIR] = None
    error: Optional[str] = None
    quality_report: Optional[Dict] = None
    execution_time: float = 0.0


class WorkflowCoordinator:
    """Coordenador determinístico do workflow de tradução.

    Controla o estado do trabalho, a ordem das etapas, retry, fallback,
    cancelamento e retomada. Os agentes executam tarefas delimitadas e
    retornam resultados estruturados.

    A sequência de agentes é:
    1. Document Analyst - Analisa a estrutura do documento
    2. Translation Planner - Planejamento da tradução
    3. Terminology Agent - Gerenciamento de terminologia
    4. Translation Agent - Tradução em si
    5. Translation Reviewer - Revisão da tradução
    6. Layout Reviewer - Revisão de layout
    7. Final QA Agent - Qualidade final
    """

    # Sequência determinística de agentes
    AGENT_SEQUENCE = [
        "document_analyst",
        "translation_planner",
        "terminology_agent",
        "translation_agent",
        "translation_reviewer",
        "layout_reviewer",
        "final_qa_agent",
    ]

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        self.state = WorkflowState(job_id=job_id)
        self.execution_history: List[AgentExecution] = []
        self._agent_results: Dict[str, Any] = {}

    def execute_workflow(self, document_ir: DocumentIR, **kwargs) -> WorkflowResult:
        """Executa o workflow completo de tradução.

        A sequência segue o padrão definido em AGENT_SEQUENCE.
        Cada agente é executado em ordem, com tratamento de erros,
        retry e fallback apropriados.
        """
        start_time = time.time()
        self.state.total_steps = len(self.AGENT_SEQUENCE)
        self.state.status = "running"
        
        logger.info(f"Iniciando workflow job {self.job_id} com {self.state.total_steps} etapas")
        
        try:
            for step_index, agent_name in enumerate(self.AGENT_SEQUENCE, 1):
                # Verificar cancelamento
                if self.state.cancellation_requested:
                    logger.info(f"Cancelamento solicitado no passo {step_index}")
                    self.state.status = "cancelled"
                    return self._result(success=False, error="Workflow cancelado pelo usuário")
                
                # Verificar limites de retry
                if self.state.retry_count >= self.state.max_retries:
                    logger.error(f"Máximo de retry ({self.state.max_retries}) atingido")
                    self.state.status = "failed"
                    return self._result(success=False, error="Limite de retry atingido")
                
                # Executar agente
                execution = AgentExecution(
                    agent_name=agent_name,
                    step=agent_name,
                    status="started",
                )
                
                try:
                    # Executar o agente correspondente
                    result = self._execute_agent(agent_name, step_index, document_ir, kwargs)
                    
                    execution.result = result
                    execution.status = "completed"
                    self.state.steps_completed = step_index
                    self.execution_history.append(execution)
                    
                    # Armazenar resultado para agentes subsequentes
                    self._agent_results[agent_name] = result
                    
                    logger.info(f"Agente {agent_name} completed no passo {step_index}")
                    
                except Exception as e:
                    logger.exception(f"Agente {agent_name} falhou no passo {step_index}")
                    execution.error = str(e)
                    execution.status = "failed"
                    
                    # Tentar retry
                    if self._should_retry(agent_name, execution):
                        execution.retry_count += 1
                        self.state.retry_count += 1
                        logger.info(f"Retry {execution.retry_count} para agente {agent_name}")
                        # Executar retry
                        try:
                            result = self._execute_agent(agent_name, step_index, document_ir, kwargs)
                            execution.result = result
                            execution.status = "completed"
                        except Exception as retry_e:
                            execution.error = f"{execution.error}; Retry falhou: {str(retry_e)}"
                            execution.status = "failed"
                    else:
                        # Não retry - marcar como falho e continuar ou parar
                        if not self._should_continue_after_failure(agent_name):
                            self.state.status = "failed"
                            return self._result(success=False, error=f"Agente {agent_name} falhou: {str(e)}")
                    
                    self.execution_history.append(execution)
                
                # Pequena pausa entre agentes para permitir monitoramento
                time.sleep(0.1)
            
            # Workflow completed successfully
            self.state.status = "completed"
            return self._result(success=True)
            
        except Exception as e:
            logger.exception("Erro inesperado no workflow")
            self.state.status = "failed"
            return self._result(success=False, error=str(e))
        
        finally:
            self.state.execution_time = time.time() - start_time
            self.state.status = "completed" if self.state.status != "failed" and self.state.status != "cancelled" else self.state.status

    def _execute_agent(self, agent_name: str, step_index: int, 
                       document_ir: DocumentIR, kwargs: Dict) -> Any:
        """Executa um agente específico pela nome."""
        
        # Mapear nome do agente para método de execução
        agent_methods = {
            "document_analyst": self._execute_document_analyst,
            "translation_planner": self._execute_translation_planner,
            "terminology_agent": self._execute_terminology_agent,
            "translation_agent": self._execute_translation_agent,
            "translation_reviewer": self._execute_translation_reviewer,
            "layout_reviewer": self._execute_layout_reviewer,
            "final_qa_agent": self._execute_final_qa_agent,
        }
        
        if agent_name not in agent_methods:
            raise ValueError(f"Agente desconhecido: {agent_name}")
        
        method = agent_methods[agent_name]
        return method(document_ir, kwargs)
    
    def _should_retry(self, agent_name: str, execution: AgentExecution) -> bool:
        """Determina se deve tentar retry para um agente que falhou."""
        # Retry nas primeiras falhas, mas não nos últimos
        if execution.retry_count < self.state.max_retries - 1:
            # Alguns agentes são mais críticos e não devem retry
            critical_agents = ["final_qa_agent"]
            if agent_name in critical_agents and execution.retry_count >= 1:
                return False
            return True
        return False
    
    def _should_continue_after_failure(self, agent_name: str) -> bool:
        """Determina se o workflow deve continuar após a falha de um agente."""
        # Alguns agentes são críticos e seu falha para o workflow
        critical_agents = ["final_qa_agent", "translation_agent"]
        if agent_name in critical_agents:
            return False
        return True
    
    def _execute_document_analyst(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Document Analyst - Analisa a estrutura do documento."""
        logger.info("Executando Document Analyst")
        
        analysis = {
            "document_type": self._classify_document(document_ir),
            "complexity": self._assess_complexity(document_ir),
            "has_tables": any(len(page.tables) > 0 for page in document_ir.pages),
            "has_images": any(len(page.images) > 0 for page in document_ir.pages),
            "has_multi_column": self._detect_multi_column(document_ir),
            "recommended_strategy": self._recommend_strategy(document_ir),
            "metadata": {
                "title": document_ir.metadata.title,
                "author": document_ir.metadata.author,
                "total_pages": len(document_ir.pages),
            }
        }
        
        return analysis
    
    def _classify_document(self, document_ir: DocumentIR) -> str:
        """Classifica o tipo de documento."""
        total_pages = len(document_ir.pages)
        total_text = sum(len(page.get_all_text()) for page in document_ir.pages)
        total_images = sum(len(page.images) for page in document_ir.pages)
        
        if total_images > total_pages * 3:
            return "image_heavy"
        elif total_text < 50 and total_images > 0:
            return "scanned"
        elif total_text > 0:
            return "textual"
        else:
            return "empty"
    
    def _assess_complexity(self, document_ir: DocumentIR) -> str:
        """Avalia a complexidade do documento."""
        complexity_score = 0
        for page in document_ir.pages:
            complexity_score += len(page.text_segments) if page.text_segments else 0
            complexity_score += len(page.tables)
            complexity_score += len(page.images)
        
        if complexity_score < 20:
            return "low"
        elif complexity_score < 100:
            return "medium"
        else:
            return "high"
    
    def _detect_multi_column(self, document_ir: DocumentIR) -> bool:
        """Detecta se o documento tem múltiplas colunas."""
        for page in document_ir.pages:
            segments = page.text_segments
            if len(segments) > 20:
                # Verificar se há textos em ambas as metades da página
                mid_x = page.width / 2
                left_text = any(s.coordinates.x0 < mid_x for s in segments)
                right_text = any(s.coordinates.x0 >= mid_x for s in segments)
                if left_text and right_text:
                    return True
        return False
    
    def _recommend_strategy(self, document_ir: DocumentIR) -> str:
        """Recomenda estratégia de tradução/reconstrução."""
        if self._has_scanned_pages(document_ir):
            return "OCR + tradução + reconstrução"
        elif self._has_many_tables(document_ir):
            return "Estratégia B - Reconstrução de blocos"
        elif self._has_multi_column(document_ir):
            return "Estratégia C - Reconstrução de página"
        else:
            return "Estratégia A - Preservação de layout"
    
    def _has_scanned_pages(self, document_ir: DocumentIR) -> bool:
        """Verifica se o documento tem páginas digitalizadas."""
        for page in document_ir.pages:
            if not page.has_text or len(page.text_segments) < 5:
                return True
        return False
    
    def _has_many_tables(self, document_ir: DocumentIR) -> bool:
        """Verifica se o documento tem muitas tabelas."""
        total_tables = sum(len(page.tables) for page in document_ir.pages)
        return total_tables > 3
    
    def _execute_translation_planner(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Translation Planner - Planejamento da tradução."""
        logger.info("Executando Translation Planner")
        
        # Determinar estratégia baseada na análise do Document Analyst
        strategy = kwargs.get("strategy", "auto")
        
        planning = {
            "selected_strategy": strategy,
            "target_language": kwargs.get("target_language", "en"),
            "source_language": kwargs.get("source_language", "pt"),
            "model_selection": self._select_model(document_ir, strategy),
            "segmentation_strategy": self._determine_segmentation(document_ir),
            "estimated_segments": len(list(self._extract_all_segments(document_ir))),
            "glossary_needs": self._identify_glossary_needs(document_ir),
            "fidelity_settings": {
                "preserve_layout": True,
                "preserve_images": True,
                "preserve_dimensions": True,
            }
        }
        
        return planning
    
    def _select_model(self, document_ir: DocumentIR, strategy: str) -> str:
        """Seleciona o modelo de IA adequado."""
        # Em um sistema real, isso consideraria o tipo de documento,
        # o par de idiomas e as capacidades do modelo disponíveis
        model_options = {
            "low": "ollama:llama3.2",  # Local, menor
            "medium": "openai:gpt-4o-mini",  # Balanceado
            "high": "openai:gpt-4o",  # Alto desempenho
            "auto": "openai:gpt-4o-mini",  # Padrão automático
        }
        return model_options.get(strategy, "openai:gpt-4o-mini")
    
    def _determine_segmentation(self, document_ir: DocumentIR) -> str:
        """Determina a estratégia de segmentação."""
        if self._has_multi_column(document_ir):
            return "by_column"  # Processar colunas separadamente
        elif self._has_many_tables(document_ir):
            return "by_block"  # Processar por blocos mantendo coordenadas
        else:
            return "by_page"  # Processar por páginas
    
    def _identify_glossary_needs(self, document_ir: DocumentIR) -> List[str]:
        """Identifica necessidades de glossário baseado no documento."""
        terms = []
        for page in document_ir.pages:
            for segment in page.text_segments:
                # Extrair termos técnicos, nomes próprios, código
                if segment.is_code or segment.is_protected:
                    terms.append("terminology_technical")
                # Verificar se há muitos números
                if len(re.findall(r'\d+', segment.text)) > 3:
                    terms.append("terminology_numbers")
        return list(set(terms))
    
    def _execute_terminology_agent(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Terminology Agent - Gerenciamento de terminologia."""
        logger.info("Executando Terminology Agent")
        
        # Extrair termos únicos do documento
        all_terms = set()
        for page in document_ir.pages:
            for segment in page.text_segments:
                if not segment.is_protected:
                    # Extrair termos potenciais (substantivos técnicos, etc.)
                    words = segment.text.split()
                    for word in words:
                        limpa = re.sub(r'[^\w]', '', word)
                        if len(limpa) > 4 and limpa.isupper():
                            all_terms.add(limpa)
                        if len(limpa) > 8:
                            all_terms.add(limpa)
        
        # Gerar sugestões de glossário
        glossary_suggestions = []
        for term in sorted(all_terms)[:20]:  # Limitar a 20 termos
            glossary_suggestions.append({
                "original": term,
                "suggestion": term,  # Em um sistema real, traduzir ou definir
                "category": "technical"
            })
        
        return {
            "detected_terms": list(all_terms),
            "glossary_suggestions": glossary_suggestions,
            "terminology_consistency": self._check_terminology_consistency(document_ir),
        }
    
    def _check_terminology_consistency(self, document_ir: DocumentIR) -> Dict:
        """Verifica consistência terminológica no documento."""
        term_occurrences: Dict[str, int] = {}
        for page in document_ir.pages:
            for segment in page.text_segments:
                words = segment.text.split()
                for word in words:
                    limpa = re.sub(r'[^\w]', '', word).lower()
                    if len(limpa) > 5:
                        term_occurrences[limpa] = term_occurrences.get(limpa, 0) + 1
        
        # Verificar se termos aparecem de forma consistente
        inconsistent = {
            term: count for term, count in term_occurrences.items() 
            if count > 1 and term.isupper()
        }
        
        return {
            "total_unique_terms": len(term_occurrences),
            "potentially_inconsistent": len(inconsistent),
            "consistency_score": round(1 - (len(inconsistent) / max(len(term_occurrences), 1)), 3)
        }
    
    def _execute_translation_agent(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Translation Agent - Tradução real do conteúdo."""
        logger.info("Executando Translation Agent")
        
        target_language = kwargs.get("target_language", "en")
        source_language = kwargs.get("source_language", "pt")
        model = kwargs.get("model", "openai:gpt-4o-mini")
        glossary = kwargs.get("glossary")
        
        # Extrair segments traduzíveis
        segments = self._extract_all_segments(document_ir)
        
        # Traduzir cada segmento
        translated_segments = []
        for i, segment in enumerate(segments):
            # Aplicar glossário se disponível
            if glossary and glossary.original:
                translated_text = self._apply_glossary_to_text(segment.original_text)
            else:
                # Em um sistema real, chamaria o modelo de IA aqui
                # Por enquanto, simular tradução
                translated_text = segment.original_text  # Placeholder
            
            segment.translated_text = translated_text
            translated_segments.append(segment)
        
        return {
            "translated_segments": len(translated_segments),
            "total_segments": len(segments),
            "model_used": model,
            "target_language": target_language,
            "progress": len(translated_segments) / max(len(segments), 1),
        }
    
    def _execute_translation_reviewer(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Translation Reviewer - Revisão da tradução."""
        logger.info("Executando Translation Reviewer")
        
        # Verificar itens como:
        # - Textos não traduzidos indevidamente
        # - Termos inconsistentes
        # - Segmentos muito curtos ou muito longos
        # - Contexto perdido
        
        segments = self._extract_all_segments(document_ir)
        issues = []
        
        for segment in segments:
            # Verificar segments muito curtos (provavelmente não traduzidos)
            if len(segment.translated_text.strip()) < 3 and len(segment.original_text.strip()) > 10:
                issues.append({
                    "type": "untranslated_segment",
                    "segment_id": segment.id,
                    "issue": "Segmento pode não ter sido traduzido",
                    "severity": "medium",
                })
            
            # Verificar termos não consistentes
            if segment.is_protected and segment.original_text != segment.translated_text:
                issues.append({
                    "type": "protected_term_changed",
                    "segment_id": segment.id,
                    "issue": "Termo protegido foi alterado",
                    "severity": "high",
                })
        
        return {
            "issues_found": issues,
            "total_segments_checked": len(segments),
            "review_score": round(1 - (len(issues) / max(len(segments), 1)), 3),
        }
    
    def _execute_layout_reviewer(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Layout Reviewer - Revisão de layout e fidelidade visual."""
        logger.info("Executando Layout Reviewer")
        
        # Verificar preservação de:
        # - Posicionamento de blocos
        # - Fontes e tamanhos
        # - Cores
        # - Hierarquia visual
        # - Tabelas e colunas
        # - Quebras de página
        
        issues = []
        
        # Verificar se há problemas de sobreposição ou conteúdo cortado
        for page in document_ir.pages:
            # Verificar blocks sobrepostos
            blocks = page.blocks if hasattr(page, 'blocks') else []
            for i, block1 in enumerate(blocks):
                for block2 in blocks[i+1:]:
                    if block1.get("coordinates") and block2.get("coordinates"):
                        overlap = block1["coordinates"].overlap(block2["coordinates"])
                        if overlap > 50:  # Limiar de sobreposição
                            issues.append({
                                "type": "block_overlap",
                                "page": page.page_number,
                                "issue": "Blocos sobrepostos detectados",
                                "severity": "high",
                                "overlap_area": overlap,
                            })
        
        # Verificar integridade das imagens
        for page in document_ir.pages:
            for image in page.images:
                if image.width < 100 or image.height < 100:
                    issues.append({
                        "type": "small_image",
                        "page": page.page_number,
                        "issue": f"Imagem pequena: {image.width}x{image.height}",
                        "severity": "medium",
                    })
        
        return {
            "layout_issues": issues,
            "total_pages_checked": len(document_ir.pages),
            "fidelity_score": round(1 - (len(issues) / max(len(document_ir.pages), 1) * 0.5), 3),
        }
    
    def _execute_final_qa_agent(self, document_ir: DocumentIR, kwargs: Dict) -> Dict:
        """Agente Final QA Agent - Qualidade final do resultado."""
        logger.info("Executando Final QA Agent")
        
        issues: List[Dict] = []
        
        # Verificações de integridade
        # 1. Verificar integridade do PDF (número de páginas)
        expected_pages = len(document_ir.pages)
        actual_pages_check = {"expected": expected_pages, "status": "ok"}
        issues.append({"type": "page_count", "issue": f"Documento tem {expected_pages} páginas", "severity": "low"})
        
        # 2. Verificar segmentos ausentes
        total_segments = sum(len(page.text_segments) for page in document_ir.pages)
        if total_segments == 0:
            issues.append({"type": "missing_segments", "issue": "Nenhum segmento de texto encontrado", "severity": "high"})
        
        # 3. Verificar conteúdo não traduzido
        for page in document_ir.pages:
            for segment in page.text_segments:
                if segment.original_text != segment.translated_text and len(segment.translated_text) < 5:
                    issues.append({
                        "type": "untranslated_content",
                        "segment_id": segment.id,
                        "issue": "Conteúdo não traduzido",
                        "severity": "medium",
                    })
        
        # 4. Consistência terminológica
        term_check = self._check_terminology_consistency(document_ir)
        if term_check["consistency_score"] < 0.8:
            issues.append({
                "type": "terminology_inconsistency",
                "issue": f"Inconsistência terminológica: {term_check['potentially_inconsistent']} termos potencialmente inconsistentes",
                "severity": "medium",
            })
        
        return {
            "quality_issues": issues,
            "total_issues": len(issues),
            "quality_score": round(1 - (len(issues) / max(total_segments if total_segments > 0 else 1, 1)) * 0.2, 3),
            "recommendations": self._generate_recommendations(issues),
        }
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Gera recomendações baseadas nos problemas encontrados."""
        recommendations = []
        
        issue_types = set(issue.get("type", "") for issue in issues)
        
        if "untranslated_content" in issue_types:
            recommendations.append("Revisar segments que não foram traduzidos completamente")
        
        if "terminology_inconsistency" in issue_types:
            recommendations.append("Aplicar glossário para consistência terminológica")
        
        if "block_overlap" in issue_types:
            recommendations.append("Revisar layout para corrigir sobreposição de blocos")
        
        if "missing_segments" in issue_types:
            recommendations.append("Extrair conteúdo adicional do documento")
        
        return recommendations
    
    def _result(self, success: bool = False, document_ir: Optional[DocumentIR] = None,
                error: Optional[str] = None, quality_report: Optional[Dict] = None) -> WorkflowResult:
        """Cria um WorkflowResult padronizado."""
        return WorkflowResult(
            job_id=self.job_id,
            success=success,
            document_ir=document_ir,
            error=error,
            quality_report=quality_report,
        )
    
    def cancel(self) -> None:
        """Solicita cancelamento do workflow."""
        self.state.cancellation_requested = True
        logger.info(f"Cancelamento solicitado para job {self.job_id}")
