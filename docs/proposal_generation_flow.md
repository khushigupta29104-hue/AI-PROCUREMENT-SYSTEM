# Proposal Generation Flow (Pipeline Detail)

```
 1. Upload Documents
 2. Knowledge Base (categorized storage)
 3. Text Extraction        (parser/pdf_parser.py or parser/docx_parser.py)
 4. Chunking                (rag/chunking.py)
 5. Embeddings              (rag/embeddings.py -- Ollama Embeddings)
 6. ChromaDB                (rag/vector_store.py, persisted in vector_db/)
 7. LangChain Retrieval     (rag/retriever.py)
 8. Ollama (local server)  (llm/ollama_client.py + llm/prompt_runner.py)
 9. Retrieve Required Fields (services/field_extraction_service.py)
10. Fill Proposal Template  (services/docx_export_service.py)
11. Generate Proposal        (DOCX saved to generated_proposals/docx/)
12. Preview                  (frontend/components/proposal_viewer.py + editable form)
13. Download DOCX / PDF      (services/pdf_export_service.py for PDF)
```

## Progress reporting contract

`services/proposal_generator_service.py`'s `ProgressReporter` calls
`progress_callback(dict)` after every stage with:
`percent`, `step_label`, `current_document`, `elapsed_display`,
`eta_display`, `retrieval_percentage`, `missing_fields` -- exactly what
`frontend/components/progress_tracker.py` needs to render live.

## Handling missing fields

If a required field cannot be confidently retrieved, it is marked `NA`
and listed in `missing_fields`. Because generation is split into two
phases, the user can fix any `NA` value directly in the editable field
form before the final DOCX/PDF is produced — no regeneration needed.
