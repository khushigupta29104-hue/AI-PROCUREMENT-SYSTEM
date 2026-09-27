# System Architecture

## Layered / Modular Design

```
frontend/ (Streamlit UI + custom CSS theme)
  pages/ (9 dashboard screens) + components/ + state/
        |
        v  calls
backend/core/ (Managers)
  document_manager | knowledge_base_manager | proposal_manager | analytics_manager
   |            |                |
   v            v                v
parser/       rag/             services/
 pdf_parser   chunking          upload_service
 docx_parser  embeddings(Ollama) field_extraction_service
 base_parser  vector_store(Chroma) proposal_generator_service
              retriever         docx_export_service
              indexer           pdf_export_service
                 |              analytics_service
                 v                   |
              ChromaDB                v
                                   llm/
                                   ollama_client
                                   prompt_runner
                                   llm_config

Cross-cutting: utils/ (logging, config, files, text, validation, ETA),
config/ (JSON configs), prompts/ (Ollama prompt text),
templates/ (5 docx templates), tests/, logs/
```

## Why this structure is scalable

1. **UI is a thin client.** `frontend/` never contains business logic — it
   only calls `backend/core/*` managers.
2. **Format-agnostic parsing.** `parser/base_parser.py`'s factory lets a
   new document format be added with one new parser class.
3. **Config-driven templates and fields.** `proposal_config.json` and
   `field_mapping.json` fully describe the 5 proposal types. Adding a 6th
   type is a config + template change only.
4. **No retraining, ever.** New documents only ever go through
   `rag/indexer.py` (chunk -> embed -> upsert). Ollama itself is never
   fine-tuned.
5. **Single embedding source of truth.** Both write (`rag/indexer.py`) and
   read (`rag/retriever.py`) paths call `rag/embeddings.py::get_embedding_function()`.
6. **Two-phase generation for editability.** `services/proposal_generator_service.py`
   splits retrieval (`resolve_fields`) from export (`finalize_and_export`)
   so the UI can let the user edit AI-retrieved values before the final
   DOCX/PDF is produced.
