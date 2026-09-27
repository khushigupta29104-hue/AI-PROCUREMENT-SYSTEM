"""
knowledge_base_manager.py
==========================
Owns the knowledge_base/ folder's sync state with ChromaDB. Provides
stats + reindex operations for the "Update Knowledge Base", "Rebuild
ChromaDB", and "Refresh Embeddings" buttons on the Knowledge Base page.
Guarantees "no retraining required": only embedding + ChromaDB upsert.
"""

from datetime import datetime
from typing import Dict

from rag.indexer import reindex_all as _reindex_all
from rag.indexer import reindex_document as _reindex_single
from rag.vector_store import get_collection_stats
from utils.config_loader import get_system_config, resolve_path
from utils.file_utils import list_files
from utils.logger import get_logger

logger = get_logger(__name__)


def get_kb_stats() -> Dict:
    """Snapshot of KB health: doc counts + vector counts, per category and overall."""
    categories = get_system_config()["knowledge_base_categories"]
    labels = get_system_config()["knowledge_base_category_labels"]
    icons = get_system_config()["knowledge_base_category_icons"]

    doc_counts = {}
    for cat in categories:
        folder = resolve_path("knowledge_base", cat)
        doc_counts[cat] = len(list_files(folder, extensions=[".pdf", ".docx"]))

    vector_stats = get_collection_stats()

    return {
        "categories": categories,
        "labels": labels,
        "icons": icons,
        "document_counts": doc_counts,
        "total_documents": sum(doc_counts.values()),
        "vector_counts_by_category": vector_stats["by_category"],
        "total_vectors": vector_stats["total_vectors"],
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def reindex_all() -> Dict:
    """Full ChromaDB rebuild from every file in knowledge_base/. Used by 'Rebuild ChromaDB'."""
    categories = get_system_config()["knowledge_base_categories"]
    kb_dir = resolve_path("knowledge_base")
    logger.warning("Starting FULL knowledge base reindex...")
    result = _reindex_all(kb_dir, categories)
    logger.info("Full reindex finished: %s", result)
    return result


def reindex_document(file_path: str, category: str) -> Dict:
    """Re-embeds a single document (used by 'Refresh Embeddings' on one file)."""
    return _reindex_single(file_path, category)
