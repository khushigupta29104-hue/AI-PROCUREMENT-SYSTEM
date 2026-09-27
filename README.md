# AI Procurement Proposal Generation System (Ollama Edition)

A **fully implemented**, enterprise-styled, **100% local** AI system
that automatically generates procurement proposals (Honeywell,
Dassault, Common Vendor, Foreign Vendor, General Notice) by retrieving
facts from your organisation's own documents (SPR, Registration,
Purchase Order, Tender, Vendor) using a RAG (Retrieval-Augmented
Generation) pipeline powered by **Ollama** — no API key, no internet
dependency once set up, no usage quota, no provider ever "retiring"
your model overnight.

Built as a B.Tech final-year project with a premium, custom-styled
Streamlit dashboard (glassmorphism cards, gradients, animations),
modular OOP-style Python architecture, and complete working code —
no placeholders, no TODOs.

---

## Why Ollama?

Every part of this system's AI runs **entirely on your own computer**:

| Task | Engine | API key needed? |
|---|---|---|
| Proposal field extraction (the "AI" part) | **Ollama** (`llama3.1:8b`, local) | **No** |
| Document embeddings (for ChromaDB search) | **Local** (`sentence-transformers`, CPU) | **No** |

No account to create, no key to manage, no rate limits, no risk of a
cloud provider changing/retiring a model overnight (which is exactly
what happened repeatedly with Gemini and Groq during development of
this project). Once installed, it works completely offline.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + dedicated `style.css` (glassmorphism / gradients) |
| Backend | Python (modular architecture) |
| LLM | Ollama (local), `llama3.1:8b` |
| Orchestration | LangChain |
| Vector Database | ChromaDB |
| Embeddings | Local HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (CPU) |
| PDF reading | PyMuPDF (`fitz`) |
| DOCX reading/writing | `python-docx` |
| PDF generation | ReportLab |
| Data processing | Pandas |
| Charts | Plotly |
| Config | JSON |
| OCR | **None** (explicitly excluded) |

---

## Getting Started

```bash
# 1. Install Ollama (one-time, separate application, not a pip package)
#    Download from: https://ollama.com/download
#    After installing, restart your computer once (ensures it's on your PATH).

# 2. Pull the model (one-time, needs internet, ~4.7 GB)
ollama pull llama3.1:8b

# 3. Start the Ollama server (keep this terminal open whenever you use the app)
ollama serve

# --- In a separate terminal, from the project folder: ---

# 4. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 5. Install Python dependencies (also downloads PyTorch for local
#    embeddings, ~1-2 GB -- this only happens once)
pip install -r requirements.txt

# 6. (Re)generate the 5 master .docx templates from config (already generated once)
python scripts/generate_templates.py

# 7. Run the app
streamlit run frontend/app.py
```

The dashboard opens at `http://localhost:8501`. The first time you
upload a document, the local embedding model (~90 MB) downloads
automatically and is cached for all future runs. After that first
setup, **no internet connection is required at all** to use the app.

**Recommended minimum hardware:** 16 GB RAM runs `llama3.1:8b`
smoothly. With 8 GB RAM it still works but may run slower — see the
Settings page to swap in a smaller model (e.g. `phi3:mini`) if needed.

---

## Dashboard (Sidebar)

| Page | Purpose |
|---|---|
| 🏠 Dashboard | KPI tiles, KB status, storage used, recent activity, quick actions |
| 📤 Upload Documents | Upload unlimited PDF/DOCX files, tag by category, auto-index |
| 📚 Knowledge Base | Browse/search, file management (rename/delete/refresh), maintenance (rebuild ChromaDB) |
| 🧾 Proposal Generator | Select type, enter references, AI retrieval with live progress, **editable field review**, export DOCX + PDF |
| 📁 Generated Proposals | Search/filter every previously generated proposal, download DOCX/PDF |
| 📊 Analytics | Plotly charts: category distribution, proposal-type distribution, upload trend, KB growth, storage, activity timeline |
| ⚙️ Settings | Edit Ollama host/model/temperature/chunking/retrieval settings live |
| ❓ Help | Step-by-step Ollama setup guide and troubleshooting FAQ |
| ℹ️ About | Tech stack, pipeline diagram, supported types/categories |

---

## Editable Proposal Preview (key feature)

Generation is split into **two phases** so you can fix any AI mistake
before downloading:

1. **Retrieve & Generate** — runs the full RAG pipeline (local
   embeddings retrieval + local Ollama extraction) and shows every
   field in an **editable form**. Any field the AI couldn't find is
   shown as `NA`.
2. **Finalize & Export** — after you review/edit the values, this
   fills the Word template and produces the final downloadable
   **DOCX** (opens directly in Microsoft Word — standard OpenXML
   format) and **PDF**.

---

## Full Folder Structure

```
ai_procurement_ollama_system/
├── README.md / requirements.txt / .env.example / .gitignore
├── run_app.sh / run_app.bat
│
├── frontend/
│   ├── app.py                          # Streamlit entrypoint (injects CSS, no API key needed)
│   ├── assets/style.css                # dedicated enterprise theme (glassmorphism, gradients)
│   ├── pages/
│   │   ├── 1_Dashboard.py
│   │   ├── 2_Upload_Documents.py
│   │   ├── 3_Knowledge_Base.py
│   │   ├── 4_Proposal_Generator.py
│   │   ├── 5_Generated_Proposals.py
│   │   ├── 6_Analytics.py
│   │   ├── 7_Settings.py
│   │   ├── 8_Help.py
│   │   └── 9_About.py
│   ├── components/                     # theme, sidebar, metric_card, progress_tracker,
│   │                                    # file_uploader_widget, proposal_viewer, status_messages, data_table
│   └── state/session_state.py
│
├── backend/core/                        # document_manager, knowledge_base_manager,
│                                         # proposal_manager, analytics_manager
│
├── rag/                                  # chunking, embeddings (LOCAL sentence-transformers),
│                                          # vector_store (ChromaDB), retriever, indexer
├── llm/                                   # llm_config, ollama_client, prompt_runner
├── parser/                                # base_parser (factory), pdf_parser (PyMuPDF), docx_parser
├── services/                              # upload_service, field_extraction_service,
│                                          # proposal_generator_service (2-phase), docx_export_service,
│                                          # pdf_export_service, analytics_service
├── prompts/                               # system_prompt.txt, field_extraction_prompt.txt,
│                                          # proposal_prompt_template.txt
│
├── templates/                             # 5 real .docx master templates
│   ├── honeywell/honeywell_template.docx
│   ├── dassault/dassault_template.docx
│   ├── common_vendor/common_vendor_template.docx
│   ├── foreign_vendor/foreign_vendor_template.docx
│   └── general_notice/general_notice_template.docx
│
├── knowledge_base/{spr,registration,purchase_order,tender,vendor}/
├── uploads/ / generated_proposals/{docx,pdf}/ / vector_db/
│
├── config/
│   ├── field_mapping.json                # exact field -> source mapping (confirmed against your filled samples)
│   ├── proposal_config.json              # 5 proposal type definitions + cover letters + icons
│   └── system_config.json                # Ollama/embeddings/Chroma/chunking/paths config
│
├── utils/                                 # logger, config_loader, file_utils, text_utils, validators, time_estimator
├── scripts/generate_templates.py          # (re)generates the 5 .docx templates from config
├── tests/                                 # pytest test suite (self-contained)
├── logs/                                  # rotating application logs
└── docs/                                  # architecture, data_flow, request_flow,
                                            # proposal_generation_flow, knowledge_base_update_flow
```

---

## How Field Retrieval Works

Every proposal type's fields are defined in `config/field_mapping.json`,
confirmed against your uploaded `*_Field_Mapping_Filled.pdf` sample
files. Each field has a `source`:

- **A knowledge-base category** (`spr`, `registration`, `purchase_order`,
  `tender`, `vendor`) → semantic ChromaDB search (local embeddings)
  scoped to that category, then the local Ollama model extracts the
  exact value from retrieved text.
- **`user_input`** → typed directly on the Proposal Generator form.
- **`ai_decision`** → the local model makes a judgement call from
  context (e.g. Vendor Status).
- **`manual_user`** → always `NA`; completed by a human (e.g. Signature).

Any field left `NA` can be fixed directly in the **editable field
form** before the final document is exported — no regeneration needed.

---

## Pipeline

```
Upload Documents → Knowledge Base → Text Extraction → Chunking →
Embeddings (local) → ChromaDB → LangChain Retrieval → Ollama (local) →
Retrieve Required Fields → Fill Proposal Template →
Generate Proposal → Preview → Download DOCX / PDF
```

New documents are indexed **incrementally** — no retraining, no full
rebuild required. The next proposal you generate automatically
benefits from any newly uploaded document. Indexing works even if the
Ollama server is temporarily not running, since embeddings run locally
too — only the field-extraction step needs Ollama live.

---

## Extensibility

- **New proposal type** → template under `templates/<new_type>/`
  (regenerate via `scripts/generate_templates.py`), one entry in
  `proposal_config.json`, one entry in `field_mapping.json`. No code changes.
- **New document category** → add to `system_config.json`'s
  `knowledge_base_categories` + create matching folders.
- **New file format** → implement `parser/base_parser.py`'s interface
  and register it in the factory.
- **Switch to a bigger/smaller local model** → change `llm_model` in
  the Settings page or `config/system_config.json`, then
  `ollama pull <new_model_name>`. No other code changes needed.

See `docs/architecture.md`, `docs/data_flow.md`, `docs/request_flow.md`,
`docs/proposal_generation_flow.md`, and `docs/knowledge_base_update_flow.md`
for deeper explanations.

---

## Notes

- **DOCX downloads open in MS Word automatically** because they use the
  standard OpenXML WordprocessingML format and MIME type — your OS
  handles opening them with whichever app is set as the default `.docx`
  handler (normally Microsoft Word).
- **Unlimited uploads**: there is no hard cap on how many documents you
  can add to the Knowledge Base; `max_files_per_upload` in Settings is
  just a soft per-batch guideline for performance.
- **Your data never leaves your computer.** Both the LLM and the
  embedding model run locally — no document text is ever sent to any
  external server.
  for  run the program type streamlit run frontend/app.py
