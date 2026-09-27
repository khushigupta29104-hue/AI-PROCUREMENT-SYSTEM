"""Unit tests for parser/docx_parser.py using an in-memory sample .docx with a paragraph and a table."""

import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from docx import Document  # noqa: E402
from parser.docx_parser import DOCXParser  # noqa: E402


def _make_sample_docx(path: str) -> None:
    doc = Document()
    doc.add_paragraph("Vendor Name: Acme Supplies Pvt Ltd")
    table = doc.add_table(rows=1, cols=2)
    cells = table.rows[0].cells
    cells[0].text = "GST"
    cells[1].text = "27ABCDE1234F1Z5"
    doc.save(path)


def test_extract_text_includes_paragraph_and_table_content():
    with tempfile.TemporaryDirectory() as tmp:
        docx_path = os.path.join(tmp, "sample.docx")
        _make_sample_docx(docx_path)
        parser = DOCXParser()
        text = parser.extract_text(docx_path)
        assert "Acme Supplies Pvt Ltd" in text
        assert "27ABCDE1234F1Z5" in text


def test_extract_metadata_reports_table_count():
    with tempfile.TemporaryDirectory() as tmp:
        docx_path = os.path.join(tmp, "sample.docx")
        _make_sample_docx(docx_path)
        parser = DOCXParser()
        meta = parser.extract_metadata(docx_path)
        assert meta["table_count"] == 1
        assert meta["file_type"] == "docx"
