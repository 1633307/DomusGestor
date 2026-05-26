from dataclasses import dataclass
from datetime import date
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 18 * mm

PAYMENT_METHOD_MAP = {
    "efectiu": "Efectiu",
    "targeta": "Targeta de crèdit",
    "transferencia": "Transferència",
    "bizum": "Pagament per mòbil",
    "altres": "Pagament a destinació",
}

DOCUMENT_TYPE_MAP = {
    "DNI": "DNI/NIF",
    "NIE": "NIE",
    "Passaport": "Passaport",
}

ACTIVE_RESERVATION_STATES = {"reservada", "lista"}


@dataclass(frozen=True)
class _SplitName:
    nom: str
    cognom1: str
    cognom2: str


def _split_full_name(nom_complet: str) -> _SplitName:
    tokens = nom_complet.strip().split()
    if not tokens:
        return _SplitName(nom="", cognom1="", cognom2="")
    nom = tokens[0]
    cognom1 = tokens[1] if len(tokens) > 1 else ""
    cognom2 = " ".join(tokens[2:]) if len(tokens) > 2 else ""
    return _SplitName(nom=nom, cognom1=cognom1, cognom2=cognom2)


def _split_residencia(residencia: str) -> tuple:
    """Return (address, municipality) from 'address, municipality' format."""
    if "," in residencia:
        parts = residencia.split(",", 1)
        return parts[0].strip(), parts[1].strip()
    return residencia.strip(), ""


def _format_date(d: Optional[date]) -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        return d
    return d.strftime("%d/%m/%Y")


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "PDFTitle",
            parent=base["Heading1"],
            fontSize=13,
            leading=16,
            spaceAfter=4 * mm,
            alignment=1,
        ),
        "section": ParagraphStyle(
            "SectionHeader",
            parent=base["Heading2"],
            fontSize=10,
            leading=13,
            spaceBefore=4 * mm,
            spaceAfter=2 * mm,
            textColor=colors.HexColor("#1a1a1a"),
        ),
        "cell": ParagraphStyle(
            "CellText",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
        ),
        "cell_bold": ParagraphStyle(
            "CellBold",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            fontName="Helvetica-Bold",
        ),
        "footer": ParagraphStyle(
            "FooterText",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            spaceBefore=6 * mm,
        ),
    }


TABLE_STYLE = TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
])

LABEL_COL_WIDTH = 62 * mm
VALUE_COL_WIDTH = PAGE_WIDTH - 2 * MARGIN - LABEL_COL_WIDTH


def _make_table(rows: List[tuple], styles: dict) -> Table:
    """Build a two-column label/value table."""
    data = [
        [
            Paragraph(label, styles["cell_bold"]),
            Paragraph(str(value), styles["cell"]),
        ]
        for label, value in rows
    ]
    table = Table(data, colWidths=[LABEL_COL_WIDTH, VALUE_COL_WIDTH])
    table.setStyle(TABLE_STYLE)
    return table


def _build_page_elements(reserva, hoste, styles: dict) -> list:
    """Build the list of flowable elements for a single guest page."""
    elements: list = []

    # Title
    elements.append(Paragraph("Registre de persones allotjades", styles["title"]))
    elements.append(Spacer(1, 2 * mm))

    # -- Dades del contracte --
    estat = reserva.estat_reserva or ""
    tipus_contracte = (
        "Contracte en curs" if estat in ACTIVE_RESERVATION_STATES else "Reserva"
    )
    metode = PAYMENT_METHOD_MAP.get(
        reserva.metode_pagament, reserva.metode_pagament or ""
    )
    num_hostes = reserva.num_hostes or reserva.hostes.count()

    elements.append(Paragraph("Dades del contracte", styles["section"]))
    elements.append(_make_table([
        ("ID policial establiment", ""),
        ("Nom de l'establiment", reserva.immoble.nom_comercial),
        ("Tipus de contracte", tipus_contracte),
        ("Número de contracte", reserva.codi_reserva),
        ("Data formalització contracte", _format_date(date.today())),
        ("Data entrada", _format_date(reserva.data_entrada)),
        ("Data sortida", _format_date(reserva.data_sortida)),
        ("Número viatgers", num_hostes),
        ("Tipus de pagament", metode),
        ("Nombre d'habitacions", reserva.immoble.num_habitacions),
        ("L'establiment disposa d'internet?", "SÍ"),
    ], styles))

    # -- Dades identificatives --
    tipus_doc = DOCUMENT_TYPE_MAP.get(hoste.tipus_document, hoste.tipus_document or "")

    elements.append(Paragraph("Dades identificatives", styles["section"]))
    elements.append(_make_table([
        ("Tipus de document", tipus_doc),
        ("Núm. document d'identitat", hoste.numero_document),
        ("Número suport document", ""),
        ("Data d'expedició", ""),
    ], styles))

    # -- Dades personals --
    name = _split_full_name(hoste.nom_complet)

    elements.append(Paragraph("Dades personals", styles["section"]))
    elements.append(_make_table([
        ("Nom", name.nom),
        ("Primer cognom", name.cognom1),
        ("Segon cognom", name.cognom2),
        ("Sexe", hoste.genere),
        ("Data de naixement", _format_date(hoste.data_naixement)),
        ("País / Nacionalitat", hoste.nacionalitat),
        ("Correu electrònic", hoste.email),
        ("Relació de parentesc", hoste.relacio_parental),
        ("Telèfon", hoste.telefon),
    ], styles))

    # -- Adreça postal --
    adreca, municipi = _split_residencia(hoste.residencia or "")

    elements.append(Paragraph("Adreça postal", styles["section"]))
    elements.append(_make_table([
        ("Adreça postal", adreca),
        ("País", "Espanya"),
        ("Província", ""),
        ("Municipi", municipi),
        ("Localitat", ""),
        ("Codi postal", ""),
    ], styles))

    # -- Signature section --
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph("Signatura:", styles["footer"]))
    elements.append(Spacer(1, 14 * mm))
    elements.append(Paragraph(
        f"{reserva.immoble.ciutat}, {_format_date(date.today())}",
        styles["footer"],
    ))

    return elements


def generate_fitxa_viatger(reserva) -> BytesIO:
    """Generate a PDF with one page per guest for the given reservation."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    styles = _build_styles()
    hostes = list(reserva.hostes.all())
    all_elements: list = []

    for i, hoste in enumerate(hostes):
        if i > 0:
            all_elements.append(PageBreak())
        all_elements.extend(_build_page_elements(reserva, hoste, styles))

    doc.build(all_elements)
    buffer.seek(0)
    return buffer
