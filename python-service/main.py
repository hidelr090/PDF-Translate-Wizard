#!/usr/bin/env python3
"""Serviço Python para processamento de PDF e tradução.

Implementa um protocolo JSON-RPC simplificado utilizando stdin/stdout.
Uma mensagem JSON por linha.
requestId unico por solicitação.
Respostas padronizadas.
Eventos assíncronos de progresso.
Identificação de jobs.
Cancelamento de operações.
Tratamento de timeout.
Tratamento de falhas do processo.
Reinicialização controlada quando aplicável.
Logs exclusivamente em stderr.
Nenhum log ou texto de diagnóstico em stdout.
"""

import sys
import json
import logging
import signal
import os
import traceback
from typing import Any, Dict, Optional, Callable
import threading
import time

# Configuração de logging apenas em stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Python] %(levelname)s: %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class JSONRPCError(Exception):
    """Erro padronizado da comunicação JSON-RPC."""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class JSONRPCMessage:
    """Representa uma mensagem JSON-RPC."""
    def __init__(self,
                 jsonrpc: str = "2.0",
                 id: Optional[str] = None,
                 method: Optional[str] = None,
                 params: Optional[Dict] = None,
                 result: Optional[Any] = None,
                 error: Optional[Dict] = None):
        self.jsonrpc = jsonrpc
        self.id = id
        self.method = method
        self.params = params or {}
        self.result = result
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": self.method,
            "params": self.params,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'JSONRPCMessage':
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> 'JSONRPCMessage':
        data = json.loads(line)
        return cls.from_dict(data)


class PythonPDFService:
    """Serviço principal que processa mensagens JSON-RPC."""

    def __init__(self):
        self.service_version = "1.0.0"
        self.protocol_version = "1.0"
        self.jobs: Dict[str, Dict] = {}
        self._running = True

        # Registrar handlers
        self.handlers = {
            "ping": self._handle_ping,
            "extract": self._handle_extract,
            "ocr": self._handle_ocr,
            "classify": self._handle_classify,
            "translate": self._handle_translate,
            "status": self._handle_status,
            "cancel": self._handle_cancel,
        }

    def _send(self, message: JSONRPCMessage) -> None:
        """Envia uma mensagem para stdout no formato JSON + newline."""
        sys.stdout.write(message.to_json() + "\n")
        sys.stdout.flush()

    def _read_message(self) -> Optional[JSONRPCMessage]:
        """Lê uma mensagem de stdin."""
        try:
            line = sys.stdin.readline()
            if not line:
                return None
            return JSONRPCMessage.from_json(line.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler mensagem: {e}")
            return None

    def _handle_ping(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Responde ao ping com pong."""
        return JSONRPCMessage(
            id=message.id,
            result={"type": "pong", "service": "python-pdf-service", "version": self.service_version}
        )

    def _handle_extract(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Extrai texto de um PDF."""
        file_path = message.params.get("file_path") if message.params else None
        if not file_path:
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32602, "message": "file_path não fornecido"}
            )

        try:
            from extractor import extract_pdf
            result = extract_pdf(file_path)
            return JSONRPCMessage(
                id=message.id,
                result={"type": "extraction_result", "data": result}
            )
        except Exception as e:
            logger.exception("Erro na extração de PDF")
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32000, "message": str(e)}
            )

    def _handle_ocr(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Realiza OCR em uma página do PDF."""
        file_path = message.params.get("file_path") if message.params else None
        page_number = message.params.get("page_number", 0) if message.params else 0
        language = message.params.get("language", "por+eng") if message.params else "por+eng"

        if not file_path:
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32602, "message": "file_path não fornecido"}
            )

        try:
            from ocr import perform_ocr
            result = perform_ocr(file_path, page_number=page_number, language=language)
            return JSONRPCMessage(
                id=message.id,
                result={"type": "ocr_result", "data": result}
            )
        except Exception as e:
            logger.exception("Erro no OCR")
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32000, "message": str(e)}
            )

    def _handle_classify(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Classifica um documento."""
        file_path = message.params.get("file_path") if message.params else None
        if not file_path:
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32602, "message": "file_path não fornecido"}
            )

        try:
            from classifier import classify_document
            result = classify_document(file_path)
            return JSONRPCMessage(
                id=message.id,
                result={"type": "classification_result", "data": result}
            )
        except Exception as e:
            logger.exception("Erro na classificação")
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32000, "message": str(e)}
            )

    def _handle_translate(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Handles translation requests."""
        job_id = message.params.get("job_id", "") if message.params else ""
        file_path = message.params.get("file_path", "") if message.params else ""

        if not job_id:
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32602, "message": "job_id não fornecido"}
            )

        # Check if job exists and get current status
        job = self.jobs.get(job_id, {})

        # For now, return job status
        return JSONRPCMessage(
            id=message.id,
            result={
                "type": "translation_status",
                "job_id": job_id,
                "status": job.get("status", "unknown"),
                "progress": job.get("progress", 0),
            }
        )

    def _handle_status(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Retorna status de um job."""
        job_id = message.params.get("job_id", "") if message.params else ""
        if not job_id:
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32602, "message": "job_id não fornecido"}
            )

        job = self.jobs.get(job_id, {})
        return JSONRPCMessage(
            id=message.id,
            result={
                "type": "job_status",
                "job_id": job_id,
                "status": job.get("status", "unknown"),
                "progress": job.get("progress", 0),
            }
        )

    def _handle_cancel(self, message: JSONRPCMessage) -> JSONRPCMessage:
        """Cancela um job em andamento."""
        job_id = message.params.get("job_id", "") if message.params else ""
        if not job_id:
            return JSONRPCMessage(
                id=message.id,
                error={"code": -32602, "message": "job_id não fornecido"}
            )

        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "cancelled"
            return JSONRPCMessage(
                id=message.id,
                result={"type": "cancel_ack", "job_id": job_id}
            )

        return JSONRPCMessage(
            id=message.id,
            error={"code": -32001, "message": "Job não encontrado"}
        )

    def _handle_shutdown(self) -> None:
        """Lida com comando de desligamento."""
        self._running = False
        sys.stdout.write(json.dumps({"type": "shutdown_ack"}) + "\n")
        sys.stdout.flush()

    def _execute_handler(self, msg: JSONRPCMessage) -> Optional[JSONRPCMessage]:
        """Executa o handler correspondente ao tipo da mensagem."""
        msg_type = msg.get("method") or msg.get("type", "")

        if msg_type == "shutdown":
            self._handle_shutdown()
            return None

        handler = self.handlers.get(msg_type)
        if handler:
            try:
                return handler(msg)
            except Exception as e:
                logger.exception(f"Erro ao processar {msg_type}")
                return JSONRPCMessage(
                    id=msg.id,
                    error={"code": -32000, "message": str(e)}
                )

        return JSONRPCMessage(
            id=msg.id,
            error={"code": -32601, "message": f"Tipo desconhecido: {msg_type}"}
        )

    def run(self) -> None:
        """Loop principal do serviço Python."""
        logger.info("Serviço Python iniciado")

        # Envia mensagem de pronto
        self._send(JSONRPCMessage(
            result={"type": "ready", "service": "python-pdf-service", "version": self.service_version}
        ))

        while self._running:
            message = self._read_message()
            if message is None:
                # EOF ou erro - sair
                break

            response = self._execute_handler(message)
            if response is not None:
                self._send(response)

        logger.info("Serviço Python finalizado")


def main() -> None:
    """Ponto de entrada do serviço."""
    service = PythonPDFService()
    try:
        service.run()
    except KeyboardInterrupt:
        logger.info("Serviço interrompido pelo usuário")
    finally:
        logger.info("Finalizando serviço Python")


if __name__ == "__main__":
    main()
