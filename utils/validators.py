"""
validators.py
==============
Input validation helpers, each returning (is_valid, error_message) so
the UI can show clear messages without inspecting raw exceptions.
"""

import os
from typing import Tuple

from utils.config_loader import get_system_config, resolve_path
from utils.file_utils import get_file_extension, get_file_hash, list_files


def is_supported_file_type(filename: str) -> Tuple[bool, str]:
    cfg = get_system_config()["file_upload"]
    allowed = cfg["allowed_extensions"]
    ext = get_file_extension(filename)
    if ext not in allowed:
        return False, f"Unsupported file type '{ext}'. Allowed types: {', '.join(allowed)}."
    return True, ""


def is_within_size_limit(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    cfg = get_system_config()["file_upload"]
    max_mb = cfg["max_file_size_mb"]
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File '{filename}' is {size_mb:.2f} MB, exceeding the {max_mb} MB limit."
    return True, ""


def is_duplicate_upload(file_bytes: bytes, category: str) -> Tuple[bool, str]:
    new_hash = get_file_hash(file_bytes)
    for base in ("uploads", "knowledge_base"):
        folder = resolve_path(base, category)
        for existing_path in list_files(folder, extensions=[".pdf", ".docx"]):
            try:
                with open(existing_path, "rb") as f:
                    existing_hash = get_file_hash(f.read())
            except OSError:
                continue
            if existing_hash == new_hash:
                return True, f"This file appears to already be uploaded as '{os.path.basename(existing_path)}'."
    return False, ""


def is_valid_pdf(file_path: str) -> Tuple[bool, str]:
    try:
        import fitz
        doc = fitz.open(file_path)
        page_count = doc.page_count
        doc.close()
        if page_count < 1:
            return False, "PDF file has no pages."
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"Invalid or corrupted PDF file: {exc}"


def is_valid_docx(file_path: str) -> Tuple[bool, str]:
    try:
        import docx
        document = docx.Document(file_path)
        _ = document.paragraphs
        return True, ""
    except Exception as exc:  # noqa: BLE001
        return False, f"Invalid or corrupted DOCX file: {exc}"


def validate_document_file(file_path: str) -> Tuple[bool, str]:
    ext = get_file_extension(file_path)
    if ext == ".pdf":
        return is_valid_pdf(file_path)
    if ext == ".docx":
        return is_valid_docx(file_path)
    return False, f"Unsupported extension '{ext}'."


def validate_required_user_inputs(user_inputs: dict, required_keys: list) -> Tuple[bool, str]:
    missing = [k for k in required_keys if not str(user_inputs.get(k, "")).strip()]
    if missing:
        return False, f"Missing required input(s): {', '.join(missing)}"
    return True, ""

