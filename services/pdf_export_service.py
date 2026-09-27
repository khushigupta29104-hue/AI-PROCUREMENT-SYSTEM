"""
pdf_export_service.py
=======================
Converts the filled proposal .docx into a PDF using ReportLab. Reads
the already-filled .docx directly (paragraphs + tables) and re-renders
that exact content as a PDF, so the system stays fully self-contained
(no external DOCX->PDF converter / OS dependency required).
"""

import os

from docx import Document as DocxDocument
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from utils.config_loader import get_system_config, resolve_path
from utils.file_utils import ensure_dir_exists
from utils.logger import get_logger

logger = get_logger(__name__)

BRAND_COLOR = colors.HexColor("#4F46E5")  # indigo, matches the dashboard theme


def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ProposalTitle", parent=styles["Heading1"],
                               alignment=TA_CENTER, textColor=BRAND_COLOR, fontSize=16, spaceAfter=6))
    styles.add(ParagraphStyle(name="ProposalSubtitle", parent=styles["Normal"],
                               alignment=TA_CENTER, fontSize=11, spaceAfter=14))
    styles.add(ParagraphStyle(name="SectionHeading", parent=styles["Heading2"],
                               textColor=BRAND_COLOR, fontSize=13, spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodyJustified", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=8))
    return styles


def _docx_table_to_reportlab_table(docx_table, col_widths=None):
    data = [[cell.text for cell in row.cells] for row in docx_table.rows]
    table = Table(data, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F0FE")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def export_pdf(docx_path: str) -> str:
    """Reads the filled .docx and re-renders its content as a PDF, saved into generated_proposals/pdf/."""
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    docx_document = DocxDocument(docx_path)
    styles = _build_styles()
    story = []
    is_first_heading = True

    for element in docx_document.element.body.iterchildren():
        tag = element.tag.rsplit("}", 1)[-1]

        if tag == "p":
            text = "".join(node.text or "" for node in element.iter() if node.tag.endswith("}t")).strip()
            if not text:
                story.append(Spacer(1, 0.2 * cm))
                continue
            if is_first_heading:
                story.append(Paragraph(text, styles["ProposalTitle"]))
                is_first_heading = False
            elif text.endswith("Master Template"):
                story.append(Paragraph(text, styles["ProposalSubtitle"]))
            elif text in ("Cover Letter", "Proposal Summary"):
                story.append(Paragraph(text, styles["SectionHeading"]))
            else:
                story.append(Paragraph(text, styles["BodyJustified"]))

        elif tag == "tbl":
            for t in docx_document.tables:
                if t._tbl is element:
                    story.append(_docx_table_to_reportlab_table(t, col_widths=[6 * cm, 9 * cm]))
                    story.append(Spacer(1, 0.4 * cm))
                    break

    output_dir = resolve_path(get_system_config()["proposal_output"]["pdf_output_dir"])
    ensure_dir_exists(output_dir)
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.pdf")

    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm, title=base_name)
    doc.build(story)

    logger.info("PDF proposal exported: '%s'", output_path)
    return output_path
