"""
pdf_parser.py
=============
Extracts text from PDF files using PyMuPDF (fitz). No OCR - assumes a
native, selectable text layer.
"""

from typing import Dict

import fitz  # PyMuPDF

from parser.base_parser import BaseParser
from utils.logger import get_logger
from utils.text_utils import clean_extracted_text

logger = get_logger(__name__)


class PDFParser(BaseParser):
    def extract_text(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to open PDF '%s': %s", file_path, exc)
            raise ValueError(f"Could not open PDF file: {exc}") from exc

        try:
            pages_text = [doc.load_page(i).get_text("text") for i in range(doc.page_count)]
            raw_text = "\n\n".join(pages_text)
        finally:
            doc.close()

        cleaned = clean_extracted_text(raw_text)
        logger.info("Extracted %d characters from PDF '%s' (%d pages)", len(cleaned), file_path, len(pages_text))
        return cleaned

    def extract_metadata(self, file_path: str) -> Dict:
        try:
            doc = fitz.open(file_path)
            meta = doc.metadata or {}
            result = {
                "page_count": doc.page_count,
                "title": meta.get("title", ""),
                "author": meta.get("author", ""),
                "file_type": "pdf",
            }
            doc.close()
            return result
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not extract metadata from PDF '%s': %s", file_path, exc)
            return {"page_count": 0, "title": "", "author": "", "file_type": "pdf"}
