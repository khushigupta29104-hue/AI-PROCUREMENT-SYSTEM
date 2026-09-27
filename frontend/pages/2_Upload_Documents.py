"""
2_Upload_Documents.py -- Upload Documents Page
=================================================
Lets the user upload PDF/DOCX documents (unlimited count), tag them
with a category, and automatically save + index them. Validates file
type/size, prevents duplicate uploads, and shows upload status,
history, date, and time.
"""

import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from backend.core.document_manager import upload_document  # noqa: E402
from frontend.components.file_uploader_widget import render_upload_form  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.status_messages import show_error, show_success  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state, log_activity  # noqa: E402

st.set_page_config(page_title="Upload Documents | ProcureAI", page_icon="📤", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("📤 Upload Documents", "Upload SPR, Registration, Purchase Order, Tender, or Vendor documents (PDF/DOCX)")

with st.container(border=True):
    uploaded_files, category = render_upload_form()

    if st.button("🚀 Process & Add to Knowledge Base", type="primary", disabled=not uploaded_files):
        results = []
        progress = st.progress(0, text="Starting upload...")

        for i, uploaded_file in enumerate(uploaded_files):
            progress.progress(int((i / len(uploaded_files)) * 100), text=f"Processing '{uploaded_file.name}'...")
            file_bytes = uploaded_file.getvalue()
            result = upload_document(file_bytes, uploaded_file.name, category)
            results.append(result)

        progress.progress(100, text="Done.")

        st.divider()
        st.subheader("📋 Upload Results")
        for result in results:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if result["success"]:
                show_success(f"{result['message']} (uploaded {timestamp}, {result['chunks_added']} chunks indexed)")
                log_activity(f"Uploaded '{result['filename']}' to {category}")
            else:
                show_error(f"{result['filename']}: {result['message']}")

st.divider()
with st.expander("ℹ️ Upload Guidelines"):
    st.markdown(
        "- Only **PDF** and **DOCX** files are supported (no OCR — files must contain real, selectable text).\n"
        "- You can upload **as many documents as you need**, one batch or many.\n"
        "- Duplicate files (identical content) are automatically rejected.\n"
        "- Once uploaded, documents are immediately available for the **next** proposal you generate — "
        "no retraining or restart required."
    )

render_sidebar_footer()
