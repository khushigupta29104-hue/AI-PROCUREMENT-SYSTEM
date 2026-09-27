# Request Flow (User Interaction -> System Response)

## Example: Generating a proposal

1. User fills the Proposal Generator form and clicks **Retrieve & Generate**.
2. Page calls `backend/core/proposal_manager.py::run_field_resolution(...)`,
   passing a `progress_callback` bound to `frontend/components/progress_tracker.py`.
3. `services/proposal_generator_service.py::resolve_fields` walks the pipeline
   stages, firing `progress_callback` after each one so the UI live-updates:
   progress bar, current step, current document, elapsed time, ETA,
   retrieval %, missing fields.
4. Field values + retrieval report are stored in `st.session_state` and
   rendered as an **editable form**.
5. User edits any field (e.g. fixes a value marked `NA`) and clicks
   **Finalize & Export**.
6. Page calls `backend/core/proposal_manager.py::run_export(...)` with the
   edited values -> `services/proposal_generator_service.py::finalize_and_export`
   -> `docx_export_service.py` -> `pdf_export_service.py`.
7. Result (docx_path, pdf_path) is stored in session state; the page shows
   a live preview (`proposal_viewer.py`) and two download buttons.
8. Any exception at any stage is caught, logged via `utils/logger.py`, and
   surfaced as a friendly error banner — never a raw stack trace.

## Example: Uploading a document

1. User selects category + files on Upload Documents, clicks
   **Process & Add to Knowledge Base**.
2. Page calls `backend/core/document_manager.py::upload_document(...)` for
   each file, which delegates to `services/upload_service.py`.
3. `upload_service` validates -> saves -> parses -> chunks -> embeds ->
   upserts into ChromaDB -> promotes into `knowledge_base/`.
4. Per-file success/failure is shown; KB stats refresh automatically on
   next page render (no caching of stale counts).
