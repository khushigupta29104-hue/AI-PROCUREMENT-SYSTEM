"""
3_Knowledge_Base.py -- Knowledge Base Page
=============================================
Displays total documents, category breakdown, recent documents,
search, delete, rename, document details/metadata, and the
"Update Knowledge Base" / "Rebuild ChromaDB" / "Refresh Embeddings"
maintenance actions.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from backend.core.document_manager import delete_document, list_documents, rename_document, search_documents  # noqa: E402
from backend.core.knowledge_base_manager import get_kb_stats, reindex_all, reindex_document  # noqa: E402
from frontend.components.data_table import render_searchable_table  # noqa: E402
from frontend.components.metric_card import render_metric_tiles  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.status_messages import show_error, show_success, show_warning  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state, log_activity  # noqa: E402

st.set_page_config(page_title="Knowledge Base | ProcureAI", page_icon="📚", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("📚 Knowledge Base", "Manage, search, and maintain your organisation's procurement documents")

kb_stats = get_kb_stats()

render_metric_tiles([
    ("📄", str(kb_stats["total_documents"]), "Total Documents"),
    ("🔗", str(kb_stats["total_vectors"]), "Indexed Chunks"),
    ("🗂️", str(len(kb_stats["categories"])), "Categories"),
])

st.divider()
st.subheader("Document Categories")
cat_cols = st.columns(len(kb_stats["categories"]))
for col, cat in zip(cat_cols, kb_stats["categories"]):
    label = kb_stats["labels"].get(cat, cat)
    icon = kb_stats["icons"].get(cat, "📄")
    col.metric(f"{icon} {label}", kb_stats["document_counts"].get(cat, 0))

st.divider()

tab_browse, tab_manage, tab_maintain = st.tabs(["🔍 Browse & Search", "🗑️ File Management", "🛠️ Maintenance"])

with tab_browse:
    filter_col, cat_col = st.columns([3, 1])
    categories_all = ["all"] + kb_stats["categories"]
    filter_cat = cat_col.selectbox(
        "Category", categories_all,
        format_func=lambda c: "All Categories" if c == "all" else kb_stats["labels"].get(c, c),
    )
    selected_category = None if filter_cat == "all" else filter_cat
    docs = search_documents("", selected_category)

    if docs:
        df = pd.DataFrame(docs)[["filename", "category", "size_mb", "modified"]]
        df["category"] = df["category"].map(lambda c: kb_stats["labels"].get(c, c))
        df.columns = ["Filename", "Category", "Size (MB)", "Uploaded At"]
        with filter_col:
            render_searchable_table(df, search_columns=["Filename", "Category"], search_label="🔍 Search documents")
    else:
        show_warning("No documents found in the knowledge base yet. Upload some from the Upload Documents page.")

with tab_manage:
    docs = list_documents()
    if not docs:
        st.info("No documents available to manage yet.")
    else:
        selected_doc = st.selectbox(
            "Select a document",
            options=docs,
            format_func=lambda d: f"{d['filename']} ({kb_stats['labels'].get(d['category'], d['category'])})",
        )

        with st.container(border=True):
            st.markdown("**📋 Document Details**")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Category", kb_stats["labels"].get(selected_doc["category"], selected_doc["category"]))
            d2.metric("Size", f"{selected_doc['size_mb']} MB")
            d3.metric("Uploaded", selected_doc["modified_date"])
            d4.metric("Time", selected_doc["modified"].split(" ")[1])

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            new_name = st.text_input("Rename to", value=os.path.splitext(selected_doc["filename"])[0])
            if st.button("✏️ Rename"):
                new_path = rename_document(selected_doc["path"], new_name)
                show_success(f"Renamed to '{os.path.basename(new_path)}'.")
                log_activity(f"Renamed document to '{os.path.basename(new_path)}'")
                st.rerun()
        with rc2:
            if st.button("🔄 Refresh Embeddings for this file"):
                with st.spinner("Re-indexing..."):
                    result = reindex_document(selected_doc["path"], selected_doc["category"])
                if result["success"]:
                    show_success(f"Refreshed embeddings ({result['chunks_added']} chunks).")
                else:
                    show_error(result["error"])
        with rc3:
            if st.button("🗑️ Delete Document", type="secondary"):
                if delete_document(selected_doc["path"], selected_doc["category"]):
                    show_success(f"Deleted '{selected_doc['filename']}' and its vectors from ChromaDB.")
                    log_activity(f"Deleted '{selected_doc['filename']}' from knowledge base")
                    st.rerun()
                else:
                    show_error("Could not delete the document (file not found).")

with tab_maintain:
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**🔄 Update Knowledge Base**")
        st.caption("Refreshes the stats shown above (documents are indexed automatically on upload).")
        if st.button("Update Knowledge Base"):
            st.rerun()
    with m2:
        st.markdown("**⚙️ Rebuild ChromaDB**")
        st.caption("Fully rebuilds the vector index from every file in knowledge_base/. Use after changing chunking settings.")
        if st.button("Rebuild ChromaDB", type="primary"):
            with st.spinner("Rebuilding the full ChromaDB index..."):
                result = reindex_all()
            if result["failed"] == 0:
                show_success(f"Rebuilt index: {result['indexed']}/{result['total_files']} documents indexed successfully.")
            else:
                show_warning(f"Rebuilt index: {result['indexed']}/{result['total_files']} succeeded; {result['failed']} failed.")
                for err in result["errors"]:
                    show_error(err)
            log_activity("Rebuilt the full ChromaDB index")

render_sidebar_footer()
