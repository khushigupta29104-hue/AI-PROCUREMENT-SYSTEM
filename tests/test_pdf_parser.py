"""Unit tests for parser/pdf_parser.py using a small in-memory generated PDF (via ReportLab)."""

import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from reportlab.pdfgen import canvas  # noqa: E402
from parser.pdf_parser import PDFParser  # noqa: E402


def _make_sample_pdf(path: str, text: str) -> None:
    c = canvas.Canvas(path)
    c.drawString(100, 750, text)
    c.save()


def test_extract_text_returns_expected_content():
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "sample.pdf")
        _make_sample_pdf(pdf_path, "PO Number: PO-2026-001")
        parser = PDFParser()
        text = parser.extract_text(pdf_path)
        assert "PO-2026-001" in text


def test_extract_metadata_returns_page_count():
    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = os.path.join(tmp, "sample.pdf")
        _make_sample_pdf(pdf_path, "Hello")
        parser = PDFParser()
        meta = parser.extract_metadata(pdf_path)
        assert meta["page_count"] == 1
        assert meta["file_type"] == "pdf"
