"""
prompt_runner.py
=================
Loads prompt templates from prompts/, fills them with retrieved
context + field metadata, sends the final prompt to the Ollama server via
llm/ollama_client.py, and parses the structured JSON response into a
plain {"value": str, "found": bool} result.
"""

import json
import os
from typing import Dict, List

from langchain_core.documents import Document

from llm.ollama_client import generate
from utils.config_loader import resolve_path, get_system_config
from utils.logger import get_logger
from utils.text_utils import extract_first_json_object

logger = get_logger(__name__)

_PROMPTS_DIR = resolve_path("prompts")
NOT_FOUND_VALUE = get_system_config().get("not_found_value", "NA")


def _load_prompt_file(filename: str) -> str:
    path = os.path.join(_PROMPTS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _format_context(chunks: List[Document]) -> str:
    if not chunks:
        return "(no relevant documents were found in the knowledge base for this field)"
    parts = []
    for i, doc in enumerate(chunks, start=1):
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Excerpt {i} - source: {source}]\n{doc.page_content}")
    return "\n\n".join(parts)


def _safe_parse(raw_response: str) -> Dict:
    json_str = extract_first_json_object(raw_response)
    parsed = json.loads(json_str)
    value = str(parsed.get("value", NOT_FOUND_VALUE)).strip() or NOT_FOUND_VALUE
    found = bool(parsed.get("found", False)) and value.upper() != "NA"
    return {"value": value if found else NOT_FOUND_VALUE, "found": found}


def extract_field_value(field_name: str, field_description: str, category: str,
                         retrieved_chunks: List[Document]) -> Dict:
    """Asks the local LLM to extract one field's value from retrieved context. Returns {"value": str, "found": bool}."""
    if not retrieved_chunks:
        return {"value": NOT_FOUND_VALUE, "found": False}

    system_prompt = _load_prompt_file("system_prompt.txt")
    template = _load_prompt_file("field_extraction_prompt.txt")
    prompt = template.format(
        system_prompt=system_prompt, field_name=field_name, field_description=field_description,
        category=category, retrieved_context=_format_context(retrieved_chunks),
    )

    try:
        raw_response = generate(prompt)
        return _safe_parse(raw_response)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to extract field '%s' via Ollama: %s", field_name, exc)
        return {"value": NOT_FOUND_VALUE, "found": False}


def decide_field_value(field_name: str, proposal_type: str, retrieved_chunks: List[Document]) -> Dict:
    """Used for 'ai_decision' fields (e.g. Vendor Status) - The local LLM makes a judgement call from context."""
    if not retrieved_chunks:
        return {"value": NOT_FOUND_VALUE, "found": False}

    system_prompt = _load_prompt_file("system_prompt.txt")
    template = _load_prompt_file("proposal_prompt_template.txt")
    prompt = template.format(
        system_prompt=system_prompt, field_name=field_name, proposal_type=proposal_type,
        retrieved_context=_format_context(retrieved_chunks),
    )

    try:
        raw_response = generate(prompt)
        return _safe_parse(raw_response)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed AI-decision extraction for field '%s': %s", field_name, exc)
        return {"value": NOT_FOUND_VALUE, "found": False}
