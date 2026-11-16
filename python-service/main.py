#!/usr/bin/env python3
"""Serviço Python para processamento de PDF e OCR.

Este serviço é empacotado junto com o Electron e se comunica via stdin/stdout
usando mensagens JSON. O usuário não precisa instalar Python manualmente.
"""

import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [Python] %(message)s')
logger = logging.getLogger(__name__)


def read_message() -> dict | None:
    """Lê uma mensagem JSON do stdin."""
    try:
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        return None


def send_message(message: dict) -> None:
    """Envia uma mensagem JSON para o stdout."""
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def handle_ping() -> dict:
    return {"type": "pong", "service": "python-pdf-service", "version": "0.1.0"}


def main() -> None:
    logger.info("Serviço Python iniciado")
    send_message({"type": "ready", "service": "python-pdf-service"})

    while True:
        message = read_message()
        if message is None:
            break

        msg_type = message.get("type")

        if msg_type == "ping":
            send_message(handle_ping())
        elif msg_type == "shutdown":
            send_message({"type": "shutdown_ack"})
            break
        else:
            send_message({"type": "error", "message": f"Tipo desconhecido: {msg_type}"})

    logger.info("Serviço Python finalizado")


if __name__ == "__main__":
    main()