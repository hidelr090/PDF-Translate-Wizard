"""Ollama Provider - Provedor de IA local via Ollama.

Implementa o protocolo AIProviderProtocol para execução de modelos Ollama
no mesmo dispositivo, sem necessidade de serviços externos.

Funcionalidades:
- Verificação de conexão com o servidor Ollama
- Listagem de modelos disponíveis
- Execução de tradução com modelo local
- Cancelamento de operações
- Tratamento de timeout
"""

import json
import logging
import subprocess
import time
from typing import Any, Dict, List, Optional

from ai_provider_layer import AIProviderProtocol, ProviderCapability, AIProviderError
from contracts.document_ir import DocumentIR

logger = logging.getLogger(__name__)


class OllamaProvider(AIProviderProtocol):
    """Provedor Ollama para execução local de modelos."""

    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3.2",
                 timeout: int = 300):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout
        self._process: Optional[subprocess.Popen] = None
        self._cancellation_flag: bool = False

    def validate_connection(self) -> bool:
        """Verifica se o servidor Ollama está rodando e acessível."""
        try:
            result = subprocess.run(
                ["curl", "-s", "-f", f"{self.base_url}/api/tags"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Não foi possível validar conexão Ollama: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """Lista modelos disponíveis no servidor Ollama."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.base_url}/api/tags"],
                capture_output=True, timeout=10
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                models = data.get("models", [])
                return [{"name": m.get("name", ""), "size": m.get("size", 0)} for m in models]
            return []
        except Exception as e:
            logger.error(f"Erro ao listar modelos Ollama: {e}")
            return []

    def get_capabilities(self) -> ProviderCapability:
        """Retorna as capacidades do provedor Ollama."""
        return ProviderCapability(
            supports_model_listing=True,
            supports_capabilities_query=False,
            supports_cancellation=True,
            max_context_tokens=32000,  # Limite típico do Llama
            supports_streaming=False,
        )

    def translate(self, document_ir: DocumentIR, target_language: str,
                  source_language: str = "pt", glossary: Optional[Dict] = None,
                  **kwargs) -> Dict[str, Any]:
        """Executa tradução usando modelo Ollama local.

        Args:
            document_ir: Documento IR com conteúdo a ser traduzido
            target_language: Idioma alvo (ex: "en")
            source_language: Idioma de origem (ex: "pt")
            glossary: Glossário de termos técnicos
            **kwargs: Parâmetros adicionais

        Returns:
            Dicionário com resultado da tradução
        """
        # Verificar se o modelo está disponível
        models = self.list_models()
        model_names = [m.get("name", "").lower() for m in models]
        
        if self.model_name.lower() not in model_names:
            # Tentar encontrar modelo similar
            available = [m for m in models if target_language in m.get("name", "").lower()]
            if available:
                self.model_name = available[0].get("name", self.model_name)
            else:
                return {
                    "success": False,
                    "error": f"Modelo '{self.model_name}' não encontrado. Modelos disponíveis: {[m.get('name') for m in models[:5]]}"
                }

        # Preparar contexto do documento
        context_text = self._prepare_context(document_ir)
        
        # Construir prompt
        prompt = self._build_prompt(context_text, target_language, source_language, glossary)
        
        # Executar modelo Ollama
        try:
            self._cancellation_flag = False
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if self._cancellation_flag:
                return {"success": False, "error": "Tradução cancelada"}
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Erro no modelo Ollama: {result.stderr[:500]}"
                }
            
            translated_text = result.stdout.strip()
            
            return {
                "success": True,
                "translated_text": translated_text,
                "model_used": self.model_name,
                "provider": "ollama",
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Timeout após {self.timeout}s. O modelo pode estar levando muito tempo para processar o contexto."
            }
        except Exception as e:
            logger.exception("Erro inesperado na tradução Ollama")
            return {
                "success": False,
                "error": str(e)
            }

    def cancel_translation(self, job_id: str) -> bool:
        """Cancela uma tradução em andamento.

        Em caso de Ollama, definição de flag de cancelamento.
        O cancelamento real depende do comportamento do modelo.
        """
        self._cancellation_flag = True
        try:
            # Tentar enviar sinal de cancelamento ao processo se houver
            if self._process and self._process.poll() is None:
                self._process.terminate()
                return True
        except Exception as e:
            logger.warning(f"Erro ao tentar cancelar: {e}")
        return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações do provedor Ollama."""
        return {
            "name": "ollama",
            "model": self.model_name,
            "base_url": self.base_url,
            "local": True,
            "type": "local_llm",
        }

    def _prepare_context(self, document_ir: DocumentIR) -> str:
        """Prepara o contexto do documento para o prompt de tradução."""
        # Extrair todo o texto do documento
        all_text = document_ir.get_all_text()
        
        # Adicionir metadados se disponíveis
        metadata_parts = []
        if document_ir.metadata.title:
            metadata_parts.append(f"Título: {document_ir.metadata.title}")
        if document_ir.metadata.author:
            metadata_parts.append(f"Autor: {document_ir.metadata.author}")
        
        context = "METADADOS DO DOCUMENTO:\n"
        if metadata_parts:
            context += "\n".join(metadata_parts) + "\n\n"
        
        context += "CONTEÚDO DO DOCUMENTO:\n"
        context += all_text if all_text else "[Nenhum texto extraível]"
        
        return context

    def _build_prompt(self, context: str, target_language: str,
                      source_language: str, glossary: Optional[Dict]) -> str:
        """Constrói o prompt para o modelo Ollama."""
        
        # Informações do glossário
        glossary_instruction = ""
        if glossary:
            glossary_instruction = "\nGLOSSÁRIO DE TERMOS:\n"
            for original, translated in glossary.items():
                glossary_instruction += f"- '{original}' deve ser traduzido como '{translated}'\n"
        
        # Instruções de preservação
        preservation_instruction = """
PRESERVAÇÃO DE INFORMAÇÕES:
- Preservar números, datas e identificadores
- Preservar fórmulas matemáticas entre delimitadores $
- Preservar código entre crases `...`
- Não traduzir termos próprios se especificado no glossário

"""

        # Instrução de linguagem
        language_instruction = f"""
TRADUÇÃO:
- Idioma de origem: {source_language}
- Idioma de destino: {target_language}
- Traduzir todo o conteúdo textual mantendo a estrutura original

"""

        prompt = f"""
{preservation_instruction}
{language_instruction}
{glossary_instruction}

CONTEXTO PARA TRADUÇÃO:
{context}

INSTRUÇÕES:
- Traduzir todo o texto acima de {source_language} para {target_language}
- Manter formatação e estrutura
- Aplicar glossário quando aplicável
- Não incluir comentários ou explicações adicionais no resultado

RESULTADO DA TRADUÇÃO:
"""

        return prompt
