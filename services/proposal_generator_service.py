"""
proposal_generator_service.py -- Pipeline Orchestrator
=========================================================
Implements the full pipeline:

    Upload Documents -> Knowledge Base -> Extract Text -> Chunk ->
    Embeddings -> ChromaDB -> LangChain Retrieval -> Ollama API ->
    Retrieve Required Fields -> Fill Proposal Template ->
    Generate Proposal -> Preview -> Download DOCX/PDF

Split into TWO phases so the UI can offer an editable preview between
retrieval and final export:

    1. resolve_fields(...)   -- retrieval + Ollama extraction only,
                                 returns field values + retrieval report.
    2. finalize_and_export(...) -- takes the (possibly user-edited)
                                 field values and produces the final
                                 DOCX + PDF files.

Both phases report live progress via a callback so the UI can render a
progress bar, current step, current document, elapsed time, estimated
remaining time, retrieval percentage, and missing fields.
"""

from typing import Callable, Dict, Optional

from services.docx_export_service import export_docx
from services.field_extraction_service import generate_field_values
from services.pdf_export_service import export_pdf
from utils.logger import get_logger
from utils.time_estimator import TimeEstimator

logger = get_logger(__name__)

# Ordered pipeline stages shown to the user during field resolution.
RESOLUTION_STAGES = [
    ("reading_documents", "Reading knowledge base documents...", None),
    ("searching_knowledge_base", "Searching Knowledge Base...", None),
    ("retrieving_spr", "Reading SPR...", "SPR documents"),
    ("retrieving_registration", "Reading Registration...", "Registration documents"),
    ("retrieving_purchase_order", "Reading Purchase Order...", "Purchase Order documents"),
    ("retrieving_tender", "Reading Tender...", "Tender documents"),
    ("retrieving_vendor", "Reading Vendor documents...", "Vendor documents"),
    ("generating_proposal", "Generating proposal with Ollama AI...", None),
]

EXPORT_STAGES = [
    ("exporting_docx", "Exporting DOCX...", None),
    ("exporting_pdf", "Exporting PDF...", None),
    ("completed", "Completed successfully!", None),
]


class ProgressReporter:
    """Wraps a user-supplied progress_callback, turning stage index into UI-ready progress info."""

    def __init__(self, progress_callback: Optional[Callable[[Dict], None]], all_stages):
        self.progress_callback = progress_callback
        self.all_stages = all_stages
        self.total_stages = len(all_stages)
        self.estimator = TimeEstimator([key for key, _, _ in all_stages])

    def report(self, stage_index: int, retrieval_pct: float = 0.0, missing_fields=None) -> None:
        if not self.progress_callback:
            return
        stage_key, stage_label, current_doc = self.all_stages[stage_index]
        percent = int(((stage_index + 1) / self.total_stages) * 100)
        eta_seconds = self.estimator.estimated_remaining_seconds(stage_index)

        self.progress_callback({
            "percent": percent,
            "step_label": stage_label,
            "current_document": current_doc or "-",
            "eta_display": self.estimator.format_seconds(eta_seconds),
            "elapsed_display": self.estimator.format_seconds(self.estimator.elapsed_seconds()),
            "retrieval_percentage": retrieval_pct,
            "missing_fields": missing_fields or [],
        })


def resolve_fields(
    proposal_type_id: str,
    reference_numbers: Dict[str, str],
    user_input_values: Dict[str, str],
    progress_callback: Optional[Callable[[Dict], None]] = None,
) -> Dict:
    """
    Phase 1: runs retrieval + Ollama field extraction only (no DOCX/PDF
    export yet), so the UI can show an editable preview of the values
    before finalizing the document.

    Returns:
        {
          "success": bool, "field_values": dict, "retrieval_percentage": float,
          "retrieved_fields": list, "missing_fields": list, "manual_fields": list,
          "error": str | None,
        }
    """
    reporter = ProgressReporter(progress_callback, RESOLUTION_STAGES)

    try:
        reporter.report(0)
        reporter.report(1)
        reporter.report(2)
        reporter.report(3)
        reporter.report(4)
        reporter.report(5)
        reporter.report(6)

        def field_progress(field_name: str, status: str) -> None:
            logger.debug("Field '%s' status=%s", field_name, status)

        extraction_result = generate_field_values(
            proposal_type_id=proposal_type_id,
            reference_numbers=reference_numbers,
            user_input_values=user_input_values,
            progress_callback=field_progress,
        )

        reporter.report(
            7,
            retrieval_pct=extraction_result["retrieval_percentage"],
            missing_fields=extraction_result["missing_fields"],
        )

        return {
            "success": True,
            "field_values": extraction_result["values"],
            "retrieval_percentage": extraction_result["retrieval_percentage"],
            "retrieved_fields": extraction_result["retrieved_fields"],
            "missing_fields": extraction_result["missing_fields"],
            "manual_fields": extraction_result["manual_fields"],
            "error": None,
        }

    except Exception as exc:  # noqa: BLE001
        logger.error("Field resolution failed for '%s': %s", proposal_type_id, exc)
        return {
            "success": False, "field_values": {}, "retrieval_percentage": 0.0,
            "retrieved_fields": [], "missing_fields": [], "manual_fields": [], "error": str(exc),
        }


def finalize_and_export(
    proposal_type_id: str,
    field_values: Dict[str, str],
    reference_numbers: Dict[str, str],
    progress_callback: Optional[Callable[[Dict], None]] = None,
) -> Dict:
    """
    Phase 2: takes the final (possibly user-edited in the Proposal
    Preview step) field values and produces the DOCX + PDF outputs.

    Returns:
        {"success": bool, "docx_path": str|None, "pdf_path": str|None, "error": str|None}
    """
    reporter = ProgressReporter(progress_callback, EXPORT_STAGES)

    try:
        docx_path = export_docx(proposal_type_id, field_values, reference_numbers)
        reporter.report(0)

        pdf_path = export_pdf(docx_path)
        reporter.report(1)
        reporter.report(2)

        return {"success": True, "docx_path": docx_path, "pdf_path": pdf_path, "error": None}

    except Exception as exc:  # noqa: BLE001
        logger.error("Export failed for '%s': %s", proposal_type_id, exc)
        return {"success": False, "docx_path": None, "pdf_path": None, "error": str(exc)}
