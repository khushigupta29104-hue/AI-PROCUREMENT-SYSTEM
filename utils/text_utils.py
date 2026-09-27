"""
text_utils.py
==============
Text cleaning/normalization applied to raw extracted text before
chunking, and small helpers used when parsing the local LLM's JSON responses.
"""

import re


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", "", text)
    lines = text.split("\n")
    cleaned_lines = [ln for ln in lines if not re.fullmatch(r"\s*(Page\s*)?\d+\s*", ln, re.IGNORECASE)]
    text = "\n".join(cleaned_lines)
    return normalize_whitespace(text)


def truncate_for_display(text: str, max_chars: int = 400) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def extract_first_json_object(text: str) -> str:
    """Extracts the first top-level {...} JSON object from a larger text blob (the local LLM sometimes wraps JSON in markdown fences despite instructions not to)."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    if start == -1:
        return text

    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return text[start:]
