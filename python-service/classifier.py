#!/usr/bin/env python3
"""Classificação da estrutura do documento PDF."""

import pdfplumber
from typing import Any, Dict, List


def classify_document(file_path: str) -> Dict[str, Any]:
    """Classifica o documento com base em sua estrutura."""
    classification = {
        "filePath": file_path,
        "documentType": "textual",
        "characteristics": [],
        "recommendedStrategy": "A",
        "needsOCR": False,
        "complexity": "low",
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            total_text_blocks = 0
            total_tables = 0
            total_images = 0
            has_scanned_pages = False
            multi_column_pages = 0

            for page in pdf.pages:
                words = page.extract_words()
                total_text_blocks += len(words)

                # Tabelas
                try:
                    tables = page.extract_tables()
                    total_tables += len(tables) if tables else 0
                except Exception:
                    pass

                # Imagens
                total_images += len(page.images)

                # Verifica se a página parece digitalizada (pouco texto selecionável)
                if len(words) < 5 and len(page.images) > 0:
                    has_scanned_pages = True

                # Verifica múltiplas colunas (aproximação simples)
                if len(words) > 20:
                    x_positions = [w["x0"] for w in words]
                    if x_positions:
                        mid = page.width / 2
                        left_count = sum(1 for x in x_positions if x < mid)
                        right_count = sum(1 for x in x_positions if x >= mid)
                        if left_count > 5 and right_count > 5:
                            multi_column_pages += 1

            # Determina tipo do documento
            if has_scanned_pages:
                classification["documentType"] = "scanned"
                classification["needsOCR"] = True
                classification["characteristics"].append("digitalizado")
                classification["recommendedStrategy"] = "C"
                classification["complexity"] = "high"
            elif total_tables > 5:
                classification["documentType"] = "tables"
                classification["characteristics"].append("tabelas")
                classification["complexity"] = "medium"
            elif multi_column_pages > total_pages / 2:
                classification["documentType"] = "multi_column"
                classification["characteristics"].append("várias colunas")
                classification["complexity"] = "medium"
            elif total_images > 10:
                classification["documentType"] = "image_heavy"
                classification["characteristics"].append("muitas imagens")
                classification["complexity"] = "medium"
            else:
                classification["documentType"] = "textual"
                classification["recommendedStrategy"] = "A"

            classification["totalPages"] = total_pages
            classification["totalTextBlocks"] = total_text_blocks
            classification["totalTables"] = total_tables
            classification["totalImages"] = total_images
            classification["multiColumnPages"] = multi_column_pages

    except Exception as e:
        classification["error"] = str(e)

    return classification


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        result = classify_document(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))