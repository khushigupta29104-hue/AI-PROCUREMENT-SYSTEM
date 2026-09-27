# Data Flow

## 1. Document Ingestion

```
User selects file(s) + category (Upload Documents page)
  -> services/upload_service.py
       -> utils/validators.py (type/size/duplicate checks)
       -> utils/file_utils.py (save to uploads/<category>/)
       -> parser/base_parser.py factory (PDF or DOCX)
       -> utils/text_utils.py (clean text)
       -> rag/indexer.py
            -> rag/chunking.py (split into chunks)
            -> rag/embeddings.py (Ollama embedding model)
            -> rag/vector_store.py (ChromaDB upsert, persisted in vector_db/)
       -> promote copy into knowledge_base/<category>/
```

## 2. Proposal Generation (Two-Phase)

```
Phase 1 - Retrieve (Proposal Generator page, "Retrieve & Generate" button)
  -> backend/core/proposal_manager.py::run_field_resolution
  -> services/proposal_generator_service.py::resolve_fields
       -> services/field_extraction_service.py
            -> rag/retriever.py (ChromaDB similarity search per field)
            -> llm/prompt_runner.py -> llm/ollama_client.py (local Ollama server)
       -> returns field values + retrieval report (%, retrieved, missing)
  -> UI renders an EDITABLE form with every field value

Phase 2 - Finalize & Export ("Finalize & Export" button)
  -> backend/core/proposal_manager.py::run_export
  -> services/proposal_generator_service.py::finalize_and_export
       -> services/docx_export_service.py (fills templates/<type>/*.docx)
       -> services/pdf_export_service.py (ReportLab renders the filled docx as PDF)
  -> UI shows preview + Download DOCX / Download PDF buttons
```

## 3. Data at Rest

| Location | Contents |
|---|---|
| `uploads/<category>/` | Raw, as-uploaded files |
| `knowledge_base/<category>/` | Promoted, successfully-indexed source documents |
| `vector_db/` | ChromaDB persistent index (Ollama embeddings + metadata) |
| `generated_proposals/docx/` | Final filled Word proposals |
| `generated_proposals/pdf/` | Final PDF exports |
| `logs/` | Application logs |
