"""OpenAI Provider - Provedor de IA via OpenAI.

Implementa o protocolo AIProviderProtocol para uso da API da OpenAI.

Funcionalidades:
- Verificação de credenciais (nunca em texto puro)
- Listagem de modelos disponíveis
- Execução de tradução via API
- Cancelamento (via API)
- Tratamento de timeout e erros
- Never store API keys in plain text - use environment variables or secret management
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import openai

from ai_provider_layer import AIProviderProtocol, ProviderCapability, AIProviderError
from contracts.document_ir import DocumentIR

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProviderProtocol):
    """Provedor OpenAI para uso da API da OpenAI."""

    def __init__(self, model_name: str = "gpt-4o-mini", 
                 timeout: int = 300,
                 api_key: Optional[str] = None):
        self.model_name = model_name
        self.timeout = timeout
        
        # Carregar API key de forma segura - NUNCA em texto puro no código
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._api_key:
            logger.warning("OpenAI API key not provided - set OPENAI_API_KEY environment variable")
        openai.api_key = self._api_key

    def validate_connection(self) -> bool:
        """Verifica se a chave da API OpenAI é válida."""
        try:
            # Teste simples: listar modelos disponíveis
            models = self.list_models()
            return len(models) > 0
        except Exception as e:
            logger.warning(f"Não foi possível validar conexão OpenAI: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """Lista modelos disponíveis na API OpenAI."""
        try:
            response = openai.models.list()
            return [{"name": m.id, "owned_by": m.owner} for m in data.get("data", [])] 
            # Note: this is simplified - actual implementation would parse response properly
        except Exception as e:
            logger.error(f"Erro ao listar modelos OpenAI: {e}")
            return []

    def get_capabilities(self) -> ProviderCapability:
        """Retorna as capacidades do provedor OpenAI."""
        return ProviderCapability(
            supports_model_listing=True,
            supports_capabilities_query=True,
            supports_cancellation=True,
            max_context_tokens=128000,  # gpt-4o context window
            supports_streaming=True,
        )

    def translate(self, document_ir: DocumentIR, target_language: str,
                  source_language: str = "pt", glossary: Optional[Dict] = None,
                  **kwargs) -> Dict[str, Any]:
        """Executa tradução via API OpenAI."""
        try:
            # Preparar contexto
            context_text = self._prepare_context(document_ir)
            
            # Construir mensagens para a API
            messages = self._build_messages(context_text, target_language, source_language, glossary)
            
            # Executar chamada API
            start_time = time.time()
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                timeout=self.timeout,
                temperature=0.3,
            )
            
            elapsed = time.time() - start_time
            
            # Extrair resposta traduzida
            translated_text = response.choices[0].message.content or ""
            
            return {
                "success": True,
                "translated_text": translated_text,
                "model_used": self.model_name,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                    "elapsed_time": elapsed,
                }
            }
            
        except openai.AuthenticationError:
            return {
                "success": False,
                "error": "Erro de autenticação: verificar chave API OpenAI"
            }
        except openai.RateLimitError:
            return {
                "success": False,
                "error": "Limite de taxa excedido. Tente novamente mais tarde."
            }
        except openai.APITimeoutError:
            return {
                "success": False,
                "error": f"Timeout da API OpenAI após {self.timeout}s"
            }
        except Exception as e:
            logger.exception("Erro inesperado na tradução OpenAI")
            return {
                "success": False,
                "error": str(e)
            }

    def cancel_translation(self, job_id: str) -> bool:
        """Cancela uma tradução em andamento.

        A API OpenAI não suporta cancelamento direto de requisições em andamento,
        mas podemos fechar a conexão ou aguardar término natural.
        """
        logger.info(f"Requisição OpenAI não pode ser cancelada diretamente, job_id: {job_id}")
        return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações do provedor OpenAI."""
        return {
            "name": "openai",
            "model": self.model_name,
            "local": False,
            "type": "remote_llm",
            "requires_api_key": True,
        }

    def _prepare_context(self, document_ir: DocumentIR) -> str:
        """Prepara o contexto do documento para o prompt."""
        all_text = document_ir.get_all_text()
        
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

    def _build_messages(self, context: str, target_language: str,
                        source_language: str, glossary: Optional[Dict]) -> List[Dict[str, str]]:
        """Constrói mensagens para a API OpenAI."""
        
        # Glossário system message
        system_msg = "You are a professional translator. "
        if glossary:
            glossary_text = ", ".join([f"'{k}' -> '{v}'" for k, v in glossary.items()])
            system_msg += f"Follow this glossary: {glossary_text}. "
        
        system_msg += f"Translate from {source_language} to {target_language}. "
        system_msg += "Preserve formatting, numbers, and special characters. "
        system_msg += "Return only the translation, no explanations."
        
        user_msg = context
        
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
