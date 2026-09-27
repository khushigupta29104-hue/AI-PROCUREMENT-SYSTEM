"""
upload_service.py
==================
End-to-end handling of a single uploaded file: validate -> check
duplicate -> save -> validate integrity -> extract+chunk+embed+upsert
(rag/indexer.py) -> promote into knowledge_base/<category>/.
"""

from typing import Dict

from rag.indexer import index_document
from utils.file_utils import copy_to_knowledge_base, save_uploaded_file
from utils.logger import get_logger
from utils.validators import (
    is_duplicate_upload,
    is_supported_file_type,
    is_within_size_limit,
    validate_document_file,
)

logger = get_logger(__name__)


def handle_uploaded_file(file_bytes: bytes, original_filename: str, category: str) -> Dict:
    """Runs the full validated ingestion pipeline for one uploaded file."""
    ok, msg = is_supported_file_type(original_filename)
    if not ok:
        logger.warning("Upload rejected (type): %s", msg)
        return {"success": False, "filename": original_filename, "message": msg, "chunks_added": 0}

    ok, msg = is_within_size_limit(file_bytes, original_filename)
    if not ok:
        logger.warning("Upload rejected (size): %s", msg)
        return {"success": False, "filename": original_filename, "message": msg, "chunks_added": 0}

    is_dup, msg = is_duplicate_upload(file_bytes, category)
    if is_dup:
        logger.warning("Upload rejected (duplicate): %s", msg)
        return {"success": False, "filename": original_filename, "message": msg, "chunks_added": 0}

    saved_path = save_uploaded_file(file_bytes, original_filename, category)

    ok, msg = validate_document_file(saved_path)
    if not ok:
        logger.error("Upload rejected (corrupted): %s", msg)
        return {"success": False, "filename": original_filename, "message": msg, "chunks_added": 0}

    index_result = index_document(saved_path, category)
    if not index_result["success"]:
        return {
            "success": False, "filename": original_filename,
            "message": f"Indexing failed: {index_result['error']}", "chunks_added": 0,
        }

    kb_path = copy_to_knowledge_base(saved_path, category)
    logger.info("Upload pipeline complete for '%s' -> %s (%d chunks)",
                original_filename, kb_path, index_result["chunks_added"])

    return {
        "success": True, "filename": original_filename,
        "message": f"'{original_filename}' uploaded and added to the '{category}' knowledge base.",
        "chunks_added": index_result["chunks_added"],
    }
