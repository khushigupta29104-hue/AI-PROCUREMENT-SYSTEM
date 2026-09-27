"""
chunking.py
===========
Splits cleaned text into overlapping chunks (LangChain's
RecursiveCharacterTextSplitter) with metadata attached, using settings
from config/system_config.json.
"""

from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from utils.config_loader import get_system_config
from utils.logger import get_logger

logger = get_logger(__name__)


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    cfg = get_system_config()["chunking"]
    return RecursiveCharacterTextSplitter(
        chunk_size=cfg["chunk_size"],
        chunk_overlap=cfg["chunk_overlap"],
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def chunk_text(text: str, metadata: Dict) -> List[Document]:
    if not text or not text.strip():
        logger.warning("chunk_text called with empty text for metadata=%s", metadata)
        return []

    splitter = get_text_splitter()
    raw_chunks = splitter.split_text(text)
    documents = [
        Document(page_content=chunk, metadata={**metadata, "chunk_index": i})
        for i, chunk in enumerate(raw_chunks)
    ]
    logger.info("Chunked document '%s' into %d chunks", metadata.get("source", "unknown"), len(documents))
    return documents
