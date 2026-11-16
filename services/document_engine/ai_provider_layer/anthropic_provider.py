"""Anthropic Provider - Provedor de IA via Anthropic.

Implementa o protocolo AIProviderProtocol para uso da API da Anthropic.

Funcionalidades:
- Verificação de credenciais (nunca em texto puro)
- Listagem de modelos disponíveis
- Execução de tradução via API
- Tratamento de timeout e erros
- Never store API keys in plain text - use environment variables or secret management
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import anthropic

from ai_provider_layer import AIProviderProtocol, ProviderCapability, AIProviderError
from contracts.document_ir import DocumentIR

logger = logging.getLogger(__name__)


class AnthropicProvider(AIProviderProtocol):
    """Provedor Anthropic para uso da API da Anthropic."""

    def __init__(self, model_name: str = "claude-3-haiku-20240307",
                 timeout: int = 300,
                 api_key: Optional[str] = None):
        self.model_name = model_name
        self.timeout = timeout
        
        # Carregar API key de forma segura - NUNCA em texto puro no código
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self._api_key:
            logger.warning("Anthropic API key not provided - set ANTHROPIC_API_KEY environment variable")
        self._client = anthropic.Anthropic(api_key=self._api_key)

    def validate_connection(self) -> bool:
        """Verifica se a chave da API Anthropic é válida."""
        try:
            # Teste simples: listar informações do modelo
            self._client.models.list()
            return True
        except Exception as e:
            logger.warning(f"Não foi possível validar conexão Anthropic: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """Lista modelos disponíveis na API Anthropic."""
        try:
            models = []
            for model in self._client.models.list():
                models.append({"name": model.id, "type": model.type})
            return models
        except Exception as e:
            logger.error(f"Erro ao listar modelos Anthropic: {e}")
            return []

    def get_capabilities(self) -> ProviderCapability:
        """Retorna as capacidades do provedor Anthropic."""
        return ProviderCapability(
            supports_model_listing=True,
            supports_capabilities_query=False,
            supports_cancellation=True,
            max_context_tokens(200000,),  # Claude 3 context window
            supports_streaming=True,
        )

    def translate(self, document_ir: DocumentIR, target_language: str,
                  source_language: str = "pt", glossary: Optional[Dict] = None,
                  **kwargs) -> Dict[str, Any]:
        """Executa tradução via API Anthropic."""
        try:
            # Preparar contexto
            context_text = self._prepare_context(document_ir)
            
            # Construir mensagens para a API
            messages = self._build_messages(context_text, target_language, source_language, glossary)
            
            # Executar chamada API
            start_time = time.time()
            
            response = self._client.messages.create(
                model=self.model_name,
                max_tokens=4000,
                temperature=0.3,
                system=self._build_system_message(glossary),
                messages=[{"role": "user", "content": context_text}],
                timeout=self.timeout,
            )
            
            elapsed = time.time() - start_time
            
            # Extrair resposta traduzida
            translated_text = ""
            for block in response.content:
                if block.type == "text":
                    translated_text += block.text
            
            return {
                "success": True,
                "translated_text": translated_text,
                "model_used": self.model_name,
                "provider": "anthropic",
                "usage": {
                    "input_tokens": response.usage.input_tokens if hasattr(response, 'usage') else 0,
                    "output_tokens": response.usage.output_tokens if hasattr(response, 'usage') else 0,
                    "elapsed_time": elapsed,
                }
            }
            
        except anthropic.AuthenticationError:
            return {
                "success": False,
                "error": "Erro de autenticação: verificar chave API Anthropic"
            }
        except anthropic.RateLimitError:
            return {
                "success": False,
                "error": "Limite de taxa excedido. Tente novamente mais tarde."
            }
        except anthropic.APITimeoutError:
            return {
                "success": False,
                "error": f"Timeout da API Anthropic após {self.timeout}s"
            }
        except Exception as e:
            logger.exception("Erro inesperado na tradução Anthropic")
            return {
                "success": False,
                "error": str(e)
            }

    def cancel_translation(self, job_id: str) -> bool:
        """Cancela uma tradução em andamento.

        A API Anthropic não suporta cancelamento direto de requisições em andamento.
        """
        logger.info(f"Requisição Anthropic não pode ser cancelada diretamente, job_id: {job_id}")
        return False

    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informações do provedor Anthropic."""
        return {
            "name": "anthropic",
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

    def _build_system_message(self, glossary: Optional[Dict]) -> str:
        """Constrói a mensagem de system para a API Anthropic."""
        system_msg = "You are a professional translator. "
        
        if glossary:
            glossary_text = ". ".join([f"'{k}' must be translated as '{v}'" for k, v in glossary.items()])
            system_msg += f"Follow this glossary: {glossary_text}. "
        
        system_msg += f"Translate from source language to {target_language}. "
        system_msg += "Preserve formatting, numbers, and special characters. "
        system_msg += "Return only the translation, no explanations."
        
        return system_msg
