"""AI Provider Layer - Camada de provedores de IA independentes.

Contratos para provedores:
- Ollama (execucao local)
- OpenAI (credenciais protegidas)
- Anthropic (credenciais protegidas)

O sistema deve permitir adicionar outros provedores sem modificar o Translation Engine.
"""

from __future__ import annotations

import abc
import json
import logging
import os
import importlib.util
from typing import Any, Dict, List, Optional

# Workspace path for dynamic imports
_WORKSPACE = "/home/hidelgardoramirez/Projetos/PDF Translate Wizard"

# Lazy-load DocumentIR using direct file import to avoid package import issues
_DOC_IR_MODULE = None
_DOC_IR_PATH = os.path.join(_WORKSPACE, "contracts", "document-ir", "document_ir.py")


def _get_document_ir():
    """Carrega DocumentIR via import direto do arquivo."""
    global _DOC_IR_MODULE
    if _DOC_IR_MODULE is None:
        if os.path.exists(_DOC_IR_PATH):
            spec = importlib.util.spec_from_file_location(
                "document_ir", _DOC_IR_PATH
            )
            _DOC_IR_MODULE = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_DOC_IR_MODULE)
        else:
            raise AIProviderError(
                code=-32602,
                message=f"Arquivo DocumentIR nao encontrado: {_DOC_IR_PATH}"
            )
    return _DOC_IR_MODULE.DocumentIR


logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Erro base da camada de provedores de IA."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class ProviderCapability:
    """Capacidades de um provedor de IA."""
    def __init__(self,
                 supports_model_listing: bool = False,
                 supports_capabilities_query: bool = False,
                 supports_cancellation: bool = False,
                 max_context_tokens: int = 100000,
                 supports_streaming: bool = False):
        self.supports_model_listing = supports_model_listing
        self.supports_capabilities_query = supports_capabilities_query
        self.supports_cancellation = supports_cancellation
        self.max_context_tokens = max_context_tokens
        self.supports_streaming = supports_streaming

    def to_dict(self) -> Dict[str, Any]:
        return {
            "supports_model_listing": self.supports_model_listing,
            "supports_capabilities_query": self.supports_capabilities_query,
            "supports_cancellation": self.supports_cancellation,
            "max_context_tokens": self.max_context_tokens,
            "supports_streaming": self.supports_streaming,
        }


class AIProviderProtocol(abc.ABC):
    """Protocolo base para todos os provedores de IA."""
    
    @abc.abstractmethod
    def validate_connection(self) -> bool:
        """Verifica se o provedor esta disponivel e conectado."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """Lista modelos disponiveis no provedor."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_capabilities(self) -> ProviderCapability:
        """Retorna as capacidades do provedor."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def translate(self,
                  document_ir: DocumentIR,
                  target_language: str,
                  source_language: str = "pt",
                  glossary: Optional[Dict] = None,
                  **kwargs) -> Dict[str, Any]:
        """Executa traducao do documento."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def cancel_translation(self, job_id: str) -> bool:
        """Cancela uma traducao em andamento."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Retorna informacoes do provedor."""
        raise NotImplementedError


class ProviderManager:
    """Gerencia o ciclo de vida dos provedores de IA."""
    _providers: Dict[str, type] = {}
    _instances: Dict[str, AIProviderProtocol] = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str, **kwargs) -> AIProviderProtocol:
        if name not in cls._providers:
            raise AIProviderError(code=-32602, message=f"Provedor '{name}' nao registrado")
        provider_class = cls._providers[name]
        instance = provider_class(**kwargs)
        cls._instances[name] = instance
        return instance
    
    @classmethod
    def get_provider(cls, name: str) -> Optional[AIProviderProtocol]:
        return cls._instances.get(name)
    
    @classmethod
    def list_registered_providers(cls) -> List[str]:
        return list(cls._providers.keys())

# Quality Engine
from services.document_engine.quality_engine import QualityEngine, QualityReport, QualityIssue  # type: ignore
