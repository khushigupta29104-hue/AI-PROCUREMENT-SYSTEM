# Knowledge Base Update Flow (No Retraining Required)

## Guarantee

Adding documents never requires retraining or fine-tuning. Ollama's LLM
and embedding models are used exactly as provided by the API; only the
ChromaDB vector index changes.

## Incremental update (automatic, on every upload)

```
New PDF/DOCX uploaded
  -> services/upload_service.py
       -> save raw file -> uploads/<category>/
       -> parser/* extracts text
       -> rag/indexer.py: chunk new text only -> embed new chunks only
          -> upsert new vectors only into the SAME ChromaDB collection
       -> backend/core/document_manager.py promotes file into knowledge_base/<category>/
  -> Knowledge base is immediately up to date; the very next proposal
     generation automatically benefits.
```

## Manual / bulk update flow

Available on the Knowledge Base page's **Maintenance** tab:
- **Update Knowledge Base** -- refreshes the displayed stats.
- **Rebuild ChromaDB** -- clears and rebuilds the entire vector index from
  every file in `knowledge_base/`. Useful after changing chunking settings.
- **Refresh Embeddings** (per-document, in File Management tab) --
  re-embeds a single file after renaming or content changes.
- **Delete Document** -- removes both the file and its vectors.

## Why this scales to new document types

`system_config.json`'s `knowledge_base_categories` list is the only place
a new document category needs to be registered; the ingestion pipeline is
category-agnostic.
