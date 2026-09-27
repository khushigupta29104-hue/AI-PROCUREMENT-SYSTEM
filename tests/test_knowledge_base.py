"""Tests filesystem-facing helpers used by backend/core/knowledge_base_manager.py that don't require ChromaDB/Ollama."""

import os
import sys
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from utils.file_utils import get_file_hash, list_files  # noqa: E402


def test_get_file_hash_is_deterministic_and_content_sensitive():
    h1 = get_file_hash(b"same content")
    h2 = get_file_hash(b"same content")
    h3 = get_file_hash(b"different content")
    assert h1 == h2
    assert h1 != h3


def test_list_files_filters_by_extension():
    with tempfile.TemporaryDirectory() as tmp:
        open(os.path.join(tmp, "a.pdf"), "w").close()
        open(os.path.join(tmp, "b.docx"), "w").close()
        open(os.path.join(tmp, "c.txt"), "w").close()
        pdf_docx_files = list_files(tmp, extensions=[".pdf", ".docx"])
        assert len(pdf_docx_files) == 2
        assert all(f.endswith((".pdf", ".docx")) for f in pdf_docx_files)
