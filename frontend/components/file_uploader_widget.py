"""
file_uploader_widget.py
========================
Wraps st.file_uploader with the category selector used on the Upload
Documents page. Supports unlimited/many files per upload (bounded only
by the configured max_files_per_upload soft limit shown as a caption).
"""

from typing import List, Tuple

import streamlit as st

from utils.config_loader import get_system_config


def render_upload_form() -> Tuple[List, str]:
    """Renders the category dropdown + multi-file uploader. Returns (uploaded_files, category)."""
    cfg = get_system_config()
    categories = cfg["knowledge_base_categories"]
    labels = cfg["knowledge_base_category_labels"]
    icons = cfg["knowledge_base_category_icons"]

    category = st.selectbox(
        "📂 Document Category",
        options=categories,
        format_func=lambda c: f"{icons.get(c, '')} {labels.get(c, c)}",
    )

    uploaded_files = st.file_uploader(
        "Drag & drop or browse PDF/DOCX documents (upload as many as you need)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
    )
    st.caption(f"No hard limit on number of files per batch (soft guideline: {cfg['file_upload']['max_files_per_upload']} at a time for best performance).")

    return uploaded_files or [], category
