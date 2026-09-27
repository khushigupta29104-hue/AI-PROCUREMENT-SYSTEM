"""
document_manager.py
====================
Facade for document operations called by the Upload Documents and
Knowledge Base pages: upload, list, delete, rename, and search.
"""

import os
from typing import Dict, List

from rag.vector_store import delete_by_source
from services.upload_service import handle_uploaded_file
from utils.config_loader import get_system_config, resolve_path
from utils.file_utils import delete_file, get_file_metadata, list_files, rename_file
from utils.logger import get_logger

logger = get_logger(__name__)


def upload_document(file_bytes: bytes, filename: str, category: str) -> Dict:
    """Delegates to services/upload_service.py for the full ingestion pipeline."""
    return handle_uploaded_file(file_bytes, filename, category)


def list_documents(category: str = None) -> List[Dict]:
    """Lists metadata for every document in the knowledge base, optionally filtered by category."""
    categories = [category] if category else get_system_config()["knowledge_base_categories"]
    documents = []
    for cat in categories:
        folder = resolve_path("knowledge_base", cat)
        for path in list_files(folder, extensions=[".pdf", ".docx"]):
            meta = get_file_metadata(path)
            meta["category"] = cat
            documents.append(meta)
    return sorted(documents, key=lambda d: d["modified"], reverse=True)


def delete_document(file_path: str, category: str) -> bool:
    """Deletes a document AND its ChromaDB vectors, keeping the two in sync."""
    filename = os.path.basename(file_path)
    delete_by_source(filename)
    deleted = delete_file(file_path)
    logger.info("Document '%s' deleted from category='%s' (vectors also removed)", filename, category)
    return deleted


def rename_document(file_path: str, new_name: str) -> str:
    """
    Renames a document on disk. NOTE: existing ChromaDB vectors still
    reference the OLD filename as their 'source' metadata; the caller
    should trigger a re-index for this file after renaming if exact
    source-name matching in the retrieval report matters.
    """
    return rename_file(file_path, new_name)


def search_documents(query: str, category: str = None) -> List[Dict]:
    """Lightweight filename-substring search, complementing the semantic ChromaDB search used during generation."""
    query_lower = query.lower().strip()
    all_docs = list_documents(category)
    if not query_lower:
        return all_docs
    return [d for d in all_docs if query_lower in d["filename"].lower()]
