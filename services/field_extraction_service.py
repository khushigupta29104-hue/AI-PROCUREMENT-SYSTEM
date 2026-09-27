"""
field_extraction_service.py
=============================
For a given proposal type, resolves every required field's value using
the strategy matching its "source" in config/field_mapping.json:

    - "user_input"   -> taken directly from the Proposal Generator form.
    - "manual_user"  -> always "NA"; filled manually later.
    - "ai_decision"  -> Ollama makes a judgement call from retrieved context.
    - a KB category  -> retrieve relevant chunks (rag/retriever.py),
                        then ask Ollama to extract the value (llm/prompt_runner.py).

Also computes the retrieval report (overall %, retrieved fields,
missing fields) shown on the Proposal Generator progress screen.
"""

from typing import Callable, Dict, List, Optional

from llm.prompt_runner import decide_field_value, extract_field_value
from rag.retriever import similarity_search
from utils.config_loader import get_field_mapping, get_system_config
from utils.logger import get_logger

logger = get_logger(__name__)

NOT_FOUND_VALUE = get_system_config().get("not_found_value", "NA")

_CATEGORY_TO_REFERENCE_KEY = {
    "spr": "spr_number",
    "registration": "registration_number",
    "purchase_order": "po_number",
    "tender": "tender_number",
}


def _build_query(field_name: str, category: str, reference_numbers: Dict[str, str]) -> str:
    ref_key = _CATEGORY_TO_REFERENCE_KEY.get(category)
    ref_value = reference_numbers.get(ref_key, "") if ref_key else ""
    return f"{field_name} {ref_value}" if ref_value else field_name


def generate_field_values(
    proposal_type_id: str,
    reference_numbers: Dict[str, str],
    user_input_values: Dict[str, str],
    progress_callback: Optional[Callable[[str, str], None]] = None,
) -> Dict:
    """
    Resolves every field required by `proposal_type_id`.

    Returns:
        {
          "values": {field_name: value, ...},
          "retrieved_fields": [...], "missing_fields": [...], "manual_fields": [...],
          "retrieval_percentage": float,
        }
    """
    mapping = get_field_mapping()
    fields = mapping["proposal_types"][proposal_type_id]["fields"]

    values: Dict[str, str] = {}
    retrieved_fields: List[str] = []
    missing_fields: List[str] = []
    manual_fields: List[str] = []
    eligible_count = 0

    for field in fields:
        field_name = field["field_name"]
        source = field["source"]

        if progress_callback:
            progress_callback(field_name, "retrieving")

        if source == "manual_user":
            values[field_name] = NOT_FOUND_VALUE
            manual_fields.append(field_name)
            continue

        eligible_count += 1

        if source == "user_input":
            value = str(user_input_values.get(field_name, "")).strip()
            if value:
                values[field_name] = value
                retrieved_fields.append(field_name)
            else:
                values[field_name] = NOT_FOUND_VALUE
                missing_fields.append(field_name)
            continue

        if source == "ai_decision":
            chunks = similarity_search(field_name, category=None)
            result = decide_field_value(field_name, proposal_type_id, chunks)
        else:
            query = _build_query(field_name, source, reference_numbers)
            chunks = similarity_search(query, category=source)
            result = extract_field_value(
                field_name=field_name,
                field_description=f"Field required for a {proposal_type_id} proposal, sourced from {source} documents.",
                category=source,
                retrieved_chunks=chunks,
            )

        values[field_name] = result["value"]
        if result["found"]:
            retrieved_fields.append(field_name)
        else:
            missing_fields.append(field_name)

        if progress_callback:
            progress_callback(field_name, "done")

    retrieval_percentage = (len(retrieved_fields) / eligible_count * 100) if eligible_count else 0.0

    logger.info(
        "Field extraction complete for '%s': %d/%d retrieved (%.1f%%), %d missing, %d manual",
        proposal_type_id, len(retrieved_fields), eligible_count, retrieval_percentage,
        len(missing_fields), len(manual_fields),
    )

    return {
        "values": values,
        "retrieved_fields": retrieved_fields,
        "missing_fields": missing_fields,
        "manual_fields": manual_fields,
        "retrieval_percentage": round(retrieval_percentage, 1),
    }
