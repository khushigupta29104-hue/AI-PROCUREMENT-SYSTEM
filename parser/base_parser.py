"""
base_parser.py
===============
Abstract interface every parser must implement, plus a factory
function get_parser_for_file() that picks the right parser by file
extension. Adding a new document format later only requires one new
parser class registered here - rag/ and services/ never change.
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseParser(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract_metadata(self, file_path: str) -> Dict:
        raise NotImplementedError


def get_parser_for_file(file_path: str) -> BaseParser:
    from parser.pdf_parser import PDFParser
    from parser.docx_parser import DOCXParser

    ext = file_path.lower().rsplit(".", 1)[-1]
    registry = {"pdf": PDFParser, "docx": DOCXParser}
    parser_cls = registry.get(ext)
    if parser_cls is None:
        raise ValueError(
            f"No parser registered for '.{ext}'. Supported: {', '.join('.' + e for e in registry)}"
        )
    return parser_cls()
