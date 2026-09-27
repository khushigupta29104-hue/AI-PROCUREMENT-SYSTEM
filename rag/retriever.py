"""
retriever.py
============
Read-path of the RAG pipeline: given a query and optional category
filter, returns the most relevant chunks from ChromaDB.
"""

from typing import List, Optional

from langchain_core.documents import Document

from rag.vector_store import get_vector_store
from utils.config_loader import get_system_config
from utils.logger import get_logger

logger = get_logger(__name__)


def similarity_search(query: str, category: Optional[str] = None, k: Optional[int] = None) -> List[Document]:
    store = get_vector_store()
    top_k = k or get_system_config()["retrieval"]["top_k"]
    search_kwargs = {"k": top_k}
    if category:
        search_kwargs["filter"] = {"category": category}
    try:
        results = store.similarity_search(query, **search_kwargs)
    except Exception as exc:  # noqa: BLE001
        logger.error("Similarity search failed for query='%s' category='%s': %s", query, category, exc)
        return []
    logger.info("Retrieved %d chunks for query='%s' category='%s'", len(results), query, category)
    return results


def has_any_documents(category: Optional[str] = None) -> bool:
    from rag.vector_store import get_collection_stats
    stats = get_collection_stats()
    if category:
        return stats["by_category"].get(category, 0) > 0
    return stats["total_vectors"] > 0
