"""
indexer.py
==========
Write-path orchestrator: turns "a document on disk" into "searchable
vectors in ChromaDB" (extract -> chunk -> embed -> upsert). No
retraining ever happens - only the ChromaDB index grows/changes.
"""

import os
from datetime import datetime
from typing import Dict, List

from parser.base_parser import get_parser_for_file
from rag.chunking import chunk_text
from rag.vector_store import delete_by_source, upsert_documents
from utils.file_utils import list_files
from utils.logger import get_logger

logger = get_logger(__name__)


def index_document(file_path: str, category: str) -> Dict:
    filename = os.path.basename(file_path)
    try:
        parser = get_parser_for_file(file_path)
        text = parser.extract_text(file_path)

        if not text.strip():
            msg = f"No extractable text found in '{filename}'. The file may be image-only (OCR is not supported)."
            logger.warning(msg)
            return {"success": False, "chunks_added": 0, "error": msg}

        metadata = {
            "source": filename,
            "category": category,
            "indexed_at": datetime.now().isoformat(timespec="seconds"),
            "file_path": file_path,
        }
        documents = chunk_text(text, metadata)

        if not documents:
            msg = f"Text extracted from '{filename}' produced zero chunks."
            logger.warning(msg)
            return {"success": False, "chunks_added": 0, "error": msg}

        upsert_documents(documents)
        logger.info("Indexed '%s' into category='%s' (%d chunks)", filename, category, len(documents))
        return {"success": True, "chunks_added": len(documents), "error": None}

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to index '%s': %s", filename, exc)
        return {"success": False, "chunks_added": 0, "error": str(exc)}


def reindex_document(file_path: str, category: str) -> Dict:
    filename = os.path.basename(file_path)
    delete_by_source(filename)
    return index_document(file_path, category)


def reindex_all(knowledge_base_dir: str, categories: List[str]) -> Dict:
    from rag.vector_store import rebuild_collection
    rebuild_collection()

    total_files = 0
    indexed = 0
    failed = 0
    errors = []

    for category in categories:
        category_dir = os.path.join(knowledge_base_dir, category)
        files = list_files(category_dir, extensions=[".pdf", ".docx"])
        for file_path in files:
            total_files += 1
            result = index_document(file_path, category)
            if result["success"]:
                indexed += 1
            else:
                failed += 1
                errors.append(f"{os.path.basename(file_path)}: {result['error']}")

    logger.info("Full reindex complete: %d/%d files indexed successfully", indexed, total_files)
    return {"total_files": total_files, "indexed": indexed, "failed": failed, "errors": errors}
