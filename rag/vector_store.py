"""
vector_store.py
================
Wraps a single persistent ChromaDB collection (via LangChain's Chroma
vectorstore) storing embeddings for ALL knowledge-base categories,
distinguished by a 'category' metadata field. Persists to vector_db/
so the knowledge base survives app restarts without re-embedding.
"""

from typing import Dict, List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from rag.embeddings import get_embedding_function
from utils.config_loader import get_system_config, resolve_path
from utils.logger import get_logger

logger = get_logger(__name__)

_vectorstore_instance: Optional[Chroma] = None


def get_vector_store() -> Chroma:
    global _vectorstore_instance
    if _vectorstore_instance is None:
        cfg = get_system_config()["vector_db"]
        persist_dir = resolve_path(cfg["persist_directory"])
        _vectorstore_instance = Chroma(
            collection_name=cfg["collection_name"],
            embedding_function=get_embedding_function(),
            persist_directory=persist_dir,
        )
        logger.info("ChromaDB vector store initialized at '%s' (collection='%s')", persist_dir, cfg["collection_name"])
    return _vectorstore_instance


def upsert_documents(documents: List[Document]) -> List[str]:
    if not documents:
        return []
    store = get_vector_store()
    ids = store.add_documents(documents)
    store.persist()
    logger.info("Upserted %d chunks into ChromaDB", len(documents))
    return ids


def delete_by_source(source_filename: str) -> None:
    store = get_vector_store()
    try:
        store._collection.delete(where={"source": source_filename})
        store.persist()
        logger.info("Deleted all vectors for source='%s'", source_filename)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to delete vectors for source='%s': %s", source_filename, exc)


def get_collection_stats() -> Dict:
    store = get_vector_store()
    try:
        raw = store._collection.get(include=["metadatas"])
        metadatas = raw.get("metadatas", []) or []
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to read collection stats: %s", exc)
        return {"total_vectors": 0, "by_category": {}}

    by_category: Dict[str, int] = {}
    for meta in metadatas:
        cat = (meta or {}).get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1

    return {"total_vectors": len(metadatas), "by_category": by_category}


def rebuild_collection() -> None:
    """Clears the whole collection - used by 'Rebuild ChromaDB'. Caller must re-add documents afterward."""
    global _vectorstore_instance
    store = get_vector_store()
    try:
        store._collection.delete(where={})
    except Exception:
        pass
    store.persist()
    _vectorstore_instance = None
    logger.warning("ChromaDB collection cleared for full rebuild.")
