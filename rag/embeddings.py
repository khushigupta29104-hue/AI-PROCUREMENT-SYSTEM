"""
embeddings.py
=============
Single source of truth for the embedding model used across the system.

Embeddings run LOCALLY via a small, free HuggingFace sentence-
transformers model (runs independent of which LLM engine is configured).
This means:
    - No API key needed for embeddings.
    - No quota/rate-limit for embeddings.
    - Works even if the Ollama server is temporarily not running
      (only proposal-field extraction needs a live Ollama server;
      document indexing/search does not).

Both the write path (rag/indexer.py) and read path (rag/retriever.py)
MUST use this exact function so vectors live in the same space.

The first call downloads the model weights (~90MB) and caches them
locally under the default HuggingFace cache directory; every call
after that runs fully offline.
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from utils.config_loader import get_system_config
from utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embedding_function() -> HuggingFaceEmbeddings:
    """Returns a cached local HuggingFaceEmbeddings instance configured from system_config.json."""
    cfg = get_system_config()["embeddings"]
    logger.info("Initializing local HuggingFaceEmbeddings model='%s' (CPU, no API key required)", cfg["model_name"])
    return HuggingFaceEmbeddings(
        model_name=cfg["model_name"],
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
