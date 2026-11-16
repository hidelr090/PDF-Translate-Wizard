"""PdfImporter - Responsável por importar e estruturar o conteúdo de documentos PDF.

Este módulo é o ponto de entrada para a extração de conteúdo de PDFs,
utilizando o PyMuPDF e pdfplumber para extração de texto, blocos, imagens e tabelas.
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the python-service to the path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.document_ir import (
    DocumentIR, DocumentMetadata, DocumentPage, TextSegment,
    DocumentImage, Table, TableCell, Coordinates, StyleInfo,
    ElementType, BlockType
)


class PdfImporter:
    """Importer de PDF que extrai a estrutura completa do documento.

    Responsável por:
    - Carregar o documento PDF
    - Extrair metadados
    - Extrair texto com coordenações e estilos
    - Extrair tabelas
    - Extrair imagens
    - Construir o Document IR
    """

    def __init__(self) -> None:
        self.extractor = PdfTextExtractor()
        self.table_extractor = TableExtractor()
        self.ocr_processor = OcrProcessor()

    def import_pdf(self, file_path: str) -> DocumentIR:
        """Importa um PDF e retorna o Document IR estruturado.

        Args:
            file_path: Caminho para o arquivo PDF

        Returns:
            DocumentIR com a estrutura completa do documento
        """
        file_path = str(Path(file_path).resolve())
        
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        # Extrair metadados e conteúdo usando PyMuPDF/pdfplumber
        pdf_data = self._extract_with_pymupdf(file_path)
        
        # Construir o Document IR
        return self._build_document_ir(file_path, pdf_data)

    def _extract_with_pymupdf(self, file_path: str) -> Dict[str, Any]:
        """Extrai dados usando PyMuPDF (fPDF2)."""
        import fitz  # PyMuPDF
        
        document = fitz.open(file_path)
        
        metadata = DocumentMetadata(
            title=document.metadata.get("title", ""),
            author=document.metadata.get("author", ""),
            subject=document.metadata.get("subject", ""),
            creator=document.metadata.get("creator", ""),
            producer=document.metadata.get("producer", ""),
            creation_date=str(document.metadata.get("creationDate", "")),
            modification_date=str(document.metadata.get("modDate", "")),
        )
        
        pages = []
        for page_num in range(len(document)):
            page = document[page_num]
            page_data = self._extract_page_data(fitz, page, page_num + 1)
            pages.append(page_data)
        
        document.close()
        return {"metadata": metadata, "pages": pages}

    def _extract_page_data(self, fitz_module, page: any, page_number: int) -> Dict[str, Any]:
        """Extrai dados de uma página específica."""
        # Texto com coordenadas
        text_blocks = []
        blocks = page.get_text("blocks")
        for block in blocks:
            # PyMuPDF blocks: [top, left, bottom, right, text, block_no, line_no, block_type]
            x0, y0, x1, y1 = block[1], block[0], block[3], block[2]
            text = block[4].strip()
            if not text:
                continue
            
            # Get font info from the page
            text_dict = page.get_text("dict")
            font_info = self._get_font_info(text_dict, text)
            
            block_type = self._classify_block(text, font_info)
            
            text_blocks.append({
                "text": text,
                "block_type": block_type,
                "coordinates": Coordinates(x0=y0, y0=x0, x1=y1, y1=x1),  # Note: PyMuPDF coords
                "font_info": font_info,
            })
        
        # Tabelas
        tables = self.table_extractor.extract_tables(page, page_number)
        
        # Imagens
        images = self._extract_images(page)
        
        return {
            "page_number": page_number,
            "width": float(page.rect.width),
            "height": float(page.rect.height),
            "orientation": "landscape" if page.rect.width > page.rect.height else "portrait",
            "text_blocks": text_blocks,
            "tables": tables,
            "images": images,
            "has_text": len(text_blocks) > 0,
        }

    def _get_font_info(self, text_dict: dict, text: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de fonte para um bloco de texto."""
        # Procurar pelo texto no dicionário
        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip() == text.strip():
                        return {
                            "family": span.get("font", ""),
                            "size": round(span.get("size", 12), 1),
                            "bold": "Bold" in span.get("font", ""),
                            "italic": "Italic" in span.get("font", ""),
                        }
        return None

    def _classify_block(self, text: str, font_info: Optional[Dict]) -> BlockType:
        """Classifica o tipo de bloco baseado no texto e fonte."""
        if not text:
            return BlockType.OTHER
        
        # Headings típicos: texto curto, fonte maior
        if len(text) < 100 and font_info and font_info.get("font_size", 0) > 14:
            return BlockType.HEADING
        
        # Verificar se parece com heading (all caps ou começa com #)
        if text.startswith("#") or (text.isupper() and len(text) > 5):
            return BlockType.HEADING
        
        # Footer: geralmente tem características específicas
        if font_info and font_size <= 10:
            return BlockType.FOOTER
        
        return BlockType.TEXT

    def _extract_images(self, page: any) -> List[Dict[str, Any]]:
        """Extrai imagens de uma página."""
        images = []
        try:
            image_list = page.get_images(full=True)
            for img_idx, img in enumerate(image_list):
                try:
                    xref = img[0]
                    pix = fitz_module.Pixmap(fitz_module.document, xref)
                    if pix.n >= 4:  # CMYK
                        pix = fitz_module.Pixmap(fitz_module.csRGB, pix)
                    
                    images.append({
                        "id": f"img_{page_number}_{img_idx}",
                        "width": float(pix.width),
                        "height": float(pix.height),
                        "original_path": f"embedded_{xref}",
                    })
                except Exception:
                    pass
        except Exception:
            pass
        
        return images


class PdfTextExtractor:
    """Extrai texto estruturado de PDFs usando PyMuPDF e pdfplumber."""
    
    def extract_page_text(self, file_path: str, page_number: int) -> Dict[str, Any]:
        """Extrai texto de uma página específica."""
        import fitz
        
        document = fitz.open(file_path)
        page = document[page_number - 1]  # 1-based to 0-based
        
        text = page.get_text("text")
        blocks = page.get_text("blocks")
        
        document.close()
        
        return {
            "page_number": page_number,
            "full_text": text,
            "blocks": blocks,
        }


class TableExtractor:
    """Extrai tabelas de documentos PDF."""
    
    def extract_tables(self, page: any, page_number: int) -> List[Table]:
        """Extrai tabelas de uma página."""
        import pdfplumber
        
        # O pdfplumber já tem métodos de extração de tabelas
        # Este é um wrapper para consistência
        tables = []
        try:
            page_tables = page.extract_tables()
            for i, table in enumerate(page_tables or []):
                if table and len(table) > 0:
                    cells = []
                    for row_idx, row in enumerate(table):
                        for col_idx, cell_text in enumerate(row):
                            if cell_text:
                                cells.append(TableCell(
                                    id=f"p{page_number}_t{i}_c{row_idx}_{col_idx}",
                                    text=str(cell_text),
                                    coordinates=Coordinates(x0=0, y0=0, x1=0, y1=0),  # Será preenchido depois
                                    row_index=row_idx,
                                    column_index=col_idx,
                                ))
                    
                    tables.append(Table(
                        id=f"p{page_number}_t{i}",
                        rows=len(table),
                        columns=len(table[0]) if table else 0,
                        cells=cells,
                        coordinates=Coordinates(x0=0, y0=0, x1=0, y1=0),
                        source_reference=f"page_{page_number}",
                    ))
        except Exception:
            pass
        
        return tables


class OcrProcessor:
    """Processador OCR para páginas digitalizadas."""
    
    def perform_ocr(self, file_path: str, page_number: int = 0, language: str = "por+eng") -> Dict[str, Any]:
        """Executa OCR em uma página ou em todas as páginas."""
        import pytesseract
        from pdf2image import convert_from_path
        
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
            
            for idx, image in enumerate(images):
                actual_page = page_number + idx if page_number > 0 else idx + 1
                try:
                    data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
                    
                    blocks = []
                    for i in range(len(data["text"])):
                        text = data["text"][i].strip()
                        if not text:
                            continue
                        
                        conf = float(data["conf"][i]) if data["conf"][i] != "-1" else 0.0
                        if conf < 30:
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
                    results["pages"].append({
                        "pageNumber": actual_page,
                        "blocks": [],
                        "error": str(e),
                    })
        except ImportError as e:
            results["error"] = f"Dependências de OCR não instaladas: {e}"
        
        return results


class DocumentNormalizer:
    """Normaliza a estrutura do Document IR para garantir consistência."""
    
    def normalize(self, document_ir: DocumentIR) -> DocumentIR:
        """Normaliza um Document IR, garantindo consistência dos dados."""
        
        # Garantir que todas as páginas têm orientação consistente
        for page in document_ir.pages:
            if page.width > page.height and page.orientation != "landscape":
                page.orientation = "landscape"
            elif page.height >= page.width and page.orientation != "portrait":
                page.orientation = "portrait"
            
            # Normalizar blocos de texto
            if page.blocks:
                for block in page.blocks:
                    self._normalize_block(block)
            
            # Garantir que segments de texto têm estilos padrão
            for segment in page.text_segments:
                if not segment.style.font_family:
                    segment.style.font_family = "Arial"
                if not segment.style.font_size:
                    segment.style.font_size = 12.0
        
        # Atualizar timestamp de modificação
        from datetime import datetime
        document_ir.modification_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        return document_ir
    
    def _normalize_block(self, block: Dict[str, Any]) -> None:
        """Normaliza um bloco individual."""
        if "coordinates" in block and block["coordinates"]:
            coords = block["coordinates"]
            # Garantir que coordenadas estão na ordem correta
            if coords.x1 < coords.x0:
                coords.x0, coords.x1 = coords.x1, coords.x0
            if coords.y1 < coords.y0:
                coords.y0, coords.y1 = coords.y1, coords.y0


class DocumentIRBuilder:
    """Construtor de Document IR a partir de dados extraídos."""
    
    def __init__(self) -> None:
        self.importer = PdfImporter()
    
    def build_from_file(self, file_path: str) -> DocumentIR:
        """Constrói um Document IR a partir de um arquivo PDF."""
        imported = self.importer.import_pdf(file_path)
        return imported
    
    def build_from_extracted(self, extracted_data: Dict[str, Any]) -> DocumentIR:
        """Constrói um Document IR a partir de dados já extraídos."""
        metadata = extracted_data.get("metadata", DocumentMetadata())
        pages_data = extracted_data.get("pages", [])
        
        pages = []
        for page_data in pages_data:
            page = DocumentPage(
                page_number=page_data.get("page_number", 1),
                width=page_data.get("width", 0.0),
                height=page_data.get("height", 0.0),
                orientation=page_data.get("orientation", "portrait"),
                blocks=page_data.get("text_blocks", []),
                images=page_data.get("images", []),
                tables=page_data.get("tables", []),
                has_text=page_data.get("has_text", False),
            )
            
            # Adicionar segments de texto a partir dos blocks
            for block in page.blocks:
                self._block_to_segment(block, page)
            
            pages.append(page)
        
        return DocumentIR(
            metadata=metadata,
            pages=pages,
        )
    
    def _block_to_segment(self, block: Dict[str, Any], page: DocumentPage) -> None:
        """Converte um bloco extraído em um TextSegment."""
        text = block.get("text", "")
        if not text:
            return
        
        coords = block.get("coordinates", Coordinates())
        font_info = block.get("font_info", {})
        
        style = StyleInfo(
            font_family=font_info.get("family", ""),
            font_size=font_info.get("size", 12.0),
            font_weight="bold" if font_info.get("bold", False) else "normal",
            font_style="italic" if font_info.get("italic", False) else "normal",
            font_color="#000000",
        )
        
        segment = TextSegment(
            id=f"p{page.page_number}_b{len(page.text_segments)}",
            text=text,
            coordinates=coords,
            style=style,
            element_type=ElementType.PARAGRAPH,
        )
        
        page.add_text_segment(segment, page.page_number)
