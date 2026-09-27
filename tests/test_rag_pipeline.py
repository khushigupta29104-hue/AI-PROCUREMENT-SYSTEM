"""Tests rag/chunking.py in isolation (pure text-splitting logic, no external services needed)."""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from rag.chunking import chunk_text  # noqa: E402


def test_chunk_text_splits_long_text_into_multiple_chunks():
    long_text = "This is a sentence about procurement. " * 200
    chunks = chunk_text(long_text, {"source": "test.pdf", "category": "tender"})
    assert len(chunks) > 1
    for i, doc in enumerate(chunks):
        assert doc.metadata["source"] == "test.pdf"
        assert doc.metadata["category"] == "tender"
        assert doc.metadata["chunk_index"] == i


def test_chunk_text_returns_empty_list_for_blank_text():
    chunks = chunk_text("   ", {"source": "empty.pdf", "category": "spr"})
    assert chunks == []
