"""Document Intermediate Representation - Contrato canônico entre extração, tradução, reconstrução e validação.

O Document IR representa a estrutura de um documento de forma independente de formato,
servindo como contrato entre as etapas de extração, tradução, reconstrução e validação.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BlockType(Enum):
    """Tipos de blocos de conteúdo no documento."""
    TEXT = "text"
    HEADING = "heading"
    FOOTER = "footer"
    TABLE = "table"
    IMAGE = "image"
    OTHER = "other"


class ElementType(Enum):
    """Tipos de elementos dentro de um bloco."""
    PARAGRAPH = "paragraph"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    IMAGE_ELEMENT = "image"


@dataclass
class Coordinates:
    """Coordenadas espaciais de um elemento no documento."""
    x0: float = 0.0
    y0: float = 0.0
    x1: float = 0.0
    y1: float = 0.0

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    def overlap(self, other: 'Coordinates') -> float:
        """Calcula a sobreposição entre dois conjuntos de coordenadas."""
        x_overlap = max(0, min(self.x1, other.x1) - max(self.x0, other.x0))
        y_overlap = max(0, min(self.y1, other.y1) - max(self.y0, other.y0))
        return x_overlap * y_overlap

    def contains(self, other: 'Coordinates') -> bool:
        """Verifica se este conjunto de coordenadas contém outro."""
        return (self.x0 <= other.x0 and self.y0 <= other.y0 and
                self.x1 >= other.x1 and self.y1 >= other.y1)


@dataclass
class StyleInfo:
    """Informações de estilo de um elemento de texto."""
    font_family: str = ""
    font_size: float = 12.0
    font_weight: str = "normal"  # normal, bold, light
    font_style: str = "normal"   # normal, italic
    font_color: str = "#000000"
    background_color: str = "transparent"
    text_align: str = "left"     # left, center, right, justify
    line_spacing: float = 1.0


@dataclass
class TextSegment:
    """Um segmento de texto com suas propriedades."""
    id: str
    text: str
    coordinates: Coordinates
    style: StyleInfo = field(default_factory=StyleInfo)
    element_type: ElementType = ElementType.PARAGRAPH
    is_protected: bool = False  # Termos protegidos (código, fórmulas, etc.)
    is_code: bool = False


@dataclass
class DocumentImage:
    """Informações de uma imagem no documento."""
    id: str
    original_path: str
    coordinates: Coordinates
    format: str = "png"
    width: float = 0.0
    height: float = 0.0
    description: str = ""  # Description for accessibility


@dataclass
class TableCell:
    """Uma célula de tabela."""
    id: str
    text: str
    coordinates: Coordinates
    row_index: int
    column_index: int
    style: StyleInfo = field(default_factory=StyleInfo)


@dataclass
class Table:
    """Uma tabela no documento."""
    id: str
    rows: int
    columns: int
    cells: List[TableCell] = field(default_factory=list)
    coordinates: Coordinates = field(default_factory=Coordinates)
    source_reference: str = ""  # Referência ao conteúdo original


@dataclass
class DocumentPage:
    """Uma página do documento."""
    page_number: int
    width: float
    height: float
    orientation: str = "portrait"  # portrait or landscape
    blocks: List[Dict[str, Any]] = field(default_factory=list)
    text_segments: List[TextSegment] = field(default_factory=list)
    images: List[DocumentImage] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    has_text: bool = False


@dataclass
class DocumentMetadata:
    """Metadados do documento."""
    title: str = ""
    author: str = ""
    subject: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    modification_date: str = ""
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentIR:
    """Representação intermediária canônica de um documento PDF.

    Este é o contrato entre:
    - Extração (PDFImporter, PdfTextExtractor, OcrProcessor)
    - Tradução (Translation Engine)
    - Reconstrução (Reconstruction Engine)
    - Validação (Quality Engine)
    """

    metadata: DocumentMetadata
    pages: List[DocumentPage]
    original_file: str = ""
    translation_status: str = "not_translated"  # not_translated, in_progress, completed, failed
    creation_time: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))
    modification_time: str = ""

    def get_page(self, page_number: int) -> Optional[DocumentPage]:
        """Obtém uma página pelo número (1-based)."""
        if 1 <= page_number <= len(self.pages):
            return self.pages[page_number - 1]
        return None

    def get_all_text(self) -> str:
        """Retorna todo o texto do documento concatenado."""
        segments = []
        for page in self.pages:
            for segment in page.text_segments:
                segments.append(segment.text)
        return " ".join(segments)

    def get_text_by_page(self, page_number: int) -> str:
        """Retorna o texto de uma página específica."""
        page = self.get_page(page_number)
        if page is None:
            return ""
        return " ".join(s.text for s in page.text_segments)

    def add_text_segment(self, segment: TextSegment, page_number: int) -> None:
        """Adiciona um segmento de texto a uma página."""
        page = self.get_page(page_number)
        if page:
            page.text_segments.append(segment)
            page.has_text = True

    def add_image(self, image: DocumentImage, page_number: int) -> None:
        """Adiciona uma imagem a uma página."""
        page = self.get_page(page_number)
        if page:
            page.images.append(image)

    def add_table(self, table: Table, page_number: int) -> None:
        """Adiciona uma tabela a uma página."""
        page = self.get_page(page_number)
        if page:
            page.tables.append(table)


import time
