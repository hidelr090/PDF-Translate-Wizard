#!/usr/bin/env python3
"""OCR condicional para páginas digitalizadas usando Tesseract."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def perform_ocr(file_path: str, page_number: int = 0, language: str = "por+eng") -> Dict[str, Any]:
    """Executa OCR em uma página específica ou em todas as páginas.

    Se page_number for 0, processa todas as páginas.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError as e:
        logger.error(f"Dependências de OCR não instaladas: {e}")
        return {
            "error": "Dependências de OCR não disponíveis. Instale pytesseract e pdf2image.",
            "blocks": [],
        }

    results = {
        "filePath": file_path,
        "language": language,
        "pages": [],
    }

    try:
        if page_number > 0:
            images = convert_from_path(file_path, first_page=page_number, last_page=page_number)
        else:
            images = convert_from_path(file_path)
    except Exception as e:
        logger.exception("Erro ao converter PDF para imagens")
        return {
            "error": f"Erro ao converter PDF para imagens: {str(e)}",
            "blocks": [],
        }

    for idx, image in enumerate(images):
        actual_page = page_number + idx if page_number > 0 else idx + 1
        try:
            # Extrai dados com coordenadas (TSV)
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)

            blocks = []
            for i in range(len(data["text"])):
                text = data["text"][i].strip()
                if not text:
                    continue

                conf = float(data["conf"][i]) if data["conf"][i] != "-1" else 0.0
                if conf < 30:  # Ignora detecções com baixa confiança
                    continue

                blocks.append({
                    "id": f"ocr_p{actual_page}_b{i}",
                    "pageNumber": actual_page,
                    "text": text,
                    "boundingBox": {
                        "x0": round(data["left"][i], 2),
                        "y0": round(data["top"][i], 2),
                        "x1": round(data["left"][i] + data["width"][i], 2),
                        "y1": round(data["top"][i] + data["height"][i], 2),
                    },
                    "font": None,
                    "alignment": "left",
                    "readingOrder": i,
                    "type": "paragraph",
                    "confidence": conf,
                })

            results["pages"].append({
                "pageNumber": actual_page,
                "blocks": blocks,
                "hasExtractableText": False,
            })
        except Exception as e:
            logger.exception(f"Erro no OCR da página {actual_page}")
            results["pages"].append({
                "pageNumber": actual_page,
                "blocks": [],
                "error": str(e),
            })

    return results


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        result = perform_ocr(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))