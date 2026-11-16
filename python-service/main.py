#!/usr/bin/env python3
"""Serviço Python para processamento de PDF e OCR."""

import sys
import json
import logging
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s [Python] %(message)s')
logger = logging.getLogger(__name__)


def read_message() -> Optional[Dict[str, Any]]:
    try:
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        return None


def send_message(message: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def handle_ping() -> Dict[str, Any]:
    return {"type": "pong", "service": "python-pdf-service", "version": "0.2.0"}


def handle_extract(message: Dict[str, Any]) -> Dict[str, Any]:
    from extractor import extract_pdf
    file_path = message.get("file_path")
    if not file_path:
        return {"type": "error", "message": "file_path não fornecido"}
    try:
        result = extract_pdf(file_path)
        return {"type": "extraction_result", "data": result}
    except Exception as e:
        logger.exception("Erro na extração de PDF")
        return {"type": "error", "message": str(e)}


def handle_ocr(message: Dict[str, Any]) -> Dict[str, Any]:
    from ocr import perform_ocr
    file_path = message.get("file_path")
    page_number = message.get("page_number", 0)
    language = message.get("language", "por+eng")
    if not file_path:
        return {"type": "error", "message": "file_path não fornecido"}
    try:
        result = perform_ocr(file_path, page_number=page_number, language=language)
        return {"type": "ocr_result", "data": result}
    except Exception as e:
        logger.exception("Erro no OCR")
        return {"type": "error", "message": str(e)}


def handle_classify(message: Dict[str, Any]) -> Dict[str, Any]:
    from classifier import classify_document
    file_path = message.get("file_path")
    if not file_path:
        return {"type": "error", "message": "file_path não fornecido"}
    try:
        result = classify_document(file_path)
        return {"type": "classification_result", "data": result}
    except Exception as e:
        logger.exception("Erro na classificação")
        return {"type": "error", "message": str(e)}


HANDLERS = {
    "ping": handle_ping,
    "extract": handle_extract,
    "ocr": handle_ocr,
    "classify": handle_classify,
}


def main() -> None:
    logger.info("Serviço Python iniciado")
    send_message({"type": "ready", "service": "python-pdf-service", "version": "0.2.0"})

    while True:
        message = read_message()
        if message is None:
            break
        msg_type = message.get("type")
        if msg_type == "shutdown":
            send_message({"type": "shutdown_ack"})
            break
        handler = HANDLERS.get(msg_type)
        if handler:
            try:
                response = handler(message)
            except Exception as e:
                logger.exception(f"Erro ao processar {msg_type}")
                response = {"type": "error", "message": str(e)}
        else:
            response = {"type": "error", "message": f"Tipo desconhecido: {msg_type}"}
        send_message(response)

    logger.info("Serviço Python finalizado")


if __name__ == "__main__":
    main()