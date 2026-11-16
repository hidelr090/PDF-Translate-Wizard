#!/usr/bin/env python3
"""Extração de texto, blocos, coordenadas, fontes e tabelas de PDFs."""

import pdfplumber
from typing import Any, Dict, List


def _infer_block_type(words, page) -> str:
    if not words:
        return "other"
    first_word = words[0]
    top = first_word.get("top", 0)
    font_size = first_word.get("size", 12)
    font_name = first_word.get("fontname", "")
    if top < 100 and font_size > 14:
        return "heading"
    page_height = page.height
    if top > page_height - 100 and font_size <= 10:
        return "footer"
    if font_size > 18:
        return "heading"
    return "paragraph"


def extract_text_blocks(page, page_number: int) -> List[Dict[str, Any]]:
    blocks = []
    words = page.extract_words(extra_attrs=["fontname", "size", "non_stroking_color"])
    if not words:
        return blocks
    lines = {}
    for word in words:
        line_key = round(word["top"], 1)
        if line_key not in lines:
            lines[line_key] = []
        lines[line_key].append(word)
    reading_order = 0
    for line_key in sorted(lines.keys()):
        line_words = sorted(lines[line_key], key=lambda w: w["x0"])
        if not line_words:
            continue
        block_type = _infer_block_type(line_words, page)
        x0 = min(w["x0"] for w in line_words)
        top = min(w["top"] for w in line_words)
        x1 = max(w["x1"] for w in line_words)
        bottom = max(w["bottom"] for w in line_words)
        text = " ".join(w["text"] for w in line_words)
        first_word = line_words[0]
        font_info = {
            "family": first_word.get("fontname", "unknown"),
            "size": round(first_word.get("size", 12), 1),
            "bold": "Bold" in first_word.get("fontname", ""),
            "italic": "Italic" in first_word.get("fontname", "") or "Oblique" in first_word.get("fontname", ""),
        }
        blocks.append({
            "id": f"p{page_number}_b{reading_order}",
            "pageNumber": page_number,
            "text": text,
            "boundingBox": {
                "x0": round(x0, 2),
                "y0": round(top, 2),
                "x1": round(x1, 2),
                "y1": round(bottom, 2),
            },
            "font": font_info,
            "alignment": "left",
            "readingOrder": reading_order,
            "type": block_type,
        })
        reading_order += 1
    return blocks


def extract_tables(page, page_number: int) -> List[Dict[str, Any]]:
    tables = []
    try:
        page_tables = page.extract_tables()
        for i, table in enumerate(page_tables or []):
            if table and len(table) > 0:
                tables.append({
                    "id": f"p{page_number}_t{i}",
                    "pageNumber": page_number,
                    "data": table,
                    "boundingBox": {
                        "x0": 0,
                        "y0": 0,
                        "x1": page.width,
                        "y1": page.height,
                    },
                })
    except Exception:
        pass
    return tables


def extract_images(page, page_number: int) -> List[Dict[str, Any]]:
    images = []
    try:
        for i, img in enumerate(page.images):
            images.append({
                "id": f"p{page_number}_img{i}",
                "pageNumber": page_number,
                "boundingBox": {
                    "x0": round(img.get("x0", 0), 2),
                    "y0": round(img.get("top", 0), 2),
                    "x1": round(img.get("x1", 0), 2),
                    "y1": round(img.get("bottom", 0), 2),
                },
            })
    except Exception:
        pass
    return images


def extract_pdf(file_path: str) -> Dict[str, Any]:
    """Extrai todo o conteúdo estruturado de um PDF."""
    document = {
        "filePath": file_path,
        "pages": [],
        "metadata": {},
        "totalPages": 0,
    }

    with pdfplumber.open(file_path) as pdf:
        document["totalPages"] = len(pdf.pages)

        if pdf.metadata:
            document["metadata"] = {
                "title": pdf.metadata.get("Title", ""),
                "author": pdf.metadata.get("Author", ""),
                "subject": pdf.metadata.get("Subject", ""),
                "creator": pdf.metadata.get("Creator", ""),
                "producer": pdf.metadata.get("Producer", ""),
            }

        for page_number, page in enumerate(pdf.pages, start=1):
            page_data = {
                "pageNumber": page_number,
                "width": round(page.width, 2),
                "height": round(page.height, 2),
                "orientation": "landscape" if page.width > page.height else "portrait",
                "textBlocks": extract_text_blocks(page, page_number),
                "tables": extract_tables(page, page_number),
                "images": extract_images(page, page_number),
                "hasExtractableText": len(page.extract_words()) > 0,
            }
            document["pages"].append(page_data)

    return document


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1:
        result = extract_pdf(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))