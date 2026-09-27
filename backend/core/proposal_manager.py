"""
proposal_manager.py
====================
Owns proposal-generation request lifecycle and the listing of
previously generated proposals for the "Generated Proposals" page.
Delegates pipeline execution to services/proposal_generator_service.py.
"""

import os
from typing import Callable, Dict, List, Optional

from services.proposal_generator_service import finalize_and_export, resolve_fields
from utils.config_loader import get_proposal_config, get_system_config, resolve_path
from utils.file_utils import get_file_metadata, list_files
from utils.logger import get_logger

logger = get_logger(__name__)


def get_available_proposal_types() -> List[Dict]:
    """Returns the list of proposal type definitions from proposal_config.json."""
    return get_proposal_config()["proposal_types"]


def run_field_resolution(
    proposal_type_id: str,
    reference_numbers: Dict[str, str],
    user_input_values: Dict[str, str],
    progress_callback: Optional[Callable[[Dict], None]] = None,
) -> Dict:
    """Phase 1: retrieval + Ollama extraction, returns field values for the editable preview."""
    logger.info("Resolving fields: type='%s' refs=%s", proposal_type_id, reference_numbers)
    return resolve_fields(proposal_type_id, reference_numbers, user_input_values, progress_callback)


def run_export(
    proposal_type_id: str,
    field_values: Dict[str, str],
    reference_numbers: Dict[str, str],
    progress_callback: Optional[Callable[[Dict], None]] = None,
) -> Dict:
    """Phase 2: exports the (possibly user-edited) field values to DOCX + PDF."""
    logger.info("Exporting final proposal: type='%s'", proposal_type_id)
    return finalize_and_export(proposal_type_id, field_values, reference_numbers, progress_callback)


def list_generated_proposals() -> List[Dict]:
    """Lists metadata for every previously generated proposal, matching .docx to its .pdf sibling."""
    cfg = get_system_config()["proposal_output"]
    docx_dir = resolve_path(cfg["docx_output_dir"])
    pdf_dir = resolve_path(cfg["pdf_output_dir"])

    results = []
    for docx_path in list_files(docx_dir, extensions=[".docx"]):
        meta = get_file_metadata(docx_path)
        base_name = os.path.splitext(os.path.basename(docx_path))[0]
        pdf_path = os.path.join(pdf_dir, f"{base_name}.pdf")
        proposal_type_id = base_name.split("_")[0]

        results.append({
            "proposal_type": proposal_type_id,
            "docx_path": docx_path,
            "pdf_path": pdf_path if os.path.exists(pdf_path) else None,
            "generated_at": meta["modified"],
            "filename_base": base_name,
        })

    return sorted(results, key=lambda r: r["generated_at"], reverse=True)
