"""
5_Generated_Proposals.py -- Generated Proposals Page
=======================================================
Lists every previously generated proposal with interactive
search/filter and download buttons for both DOCX and PDF formats.
Downloaded DOCX files open directly in Microsoft Word since they use
the standard .docx (OpenXML WordprocessingML) format and MIME type --
the browser/OS handles opening them in Word automatically.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from backend.core.proposal_manager import get_available_proposal_types, list_generated_proposals  # noqa: E402
from frontend.components.metric_card import render_metric_tiles  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402

st.set_page_config(page_title="Generated Proposals | ProcureAI", page_icon="📁", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("📁 Generated Proposals", "Browse and download every proposal your team has generated")

proposals = list_generated_proposals()
type_labels = {t["id"]: t["display_name"] for t in get_available_proposal_types()}
type_icons = {t["id"]: t.get("icon", "🧾") for t in get_available_proposal_types()}

render_metric_tiles([
    ("🧾", str(len(proposals)), "Total Proposals"),
    ("🏢", str(len(set(p["proposal_type"] for p in proposals))), "Types Used"),
])

st.divider()

if not proposals:
    st.info("No proposals have been generated yet. Head to the Proposal Generator page to create your first one.")
else:
    fc1, fc2 = st.columns([1, 3])
    filter_type = fc1.selectbox(
        "Filter by type",
        options=["all"] + list(type_labels.keys()),
        format_func=lambda t: "All Types" if t == "all" else f"{type_icons.get(t,'')} {type_labels.get(t, t)}",
    )
    search_query = fc2.text_input("🔍 Search by filename", "")

    filtered = proposals if filter_type == "all" else [p for p in proposals if p["proposal_type"] == filter_type]
    if search_query:
        filtered = [p for p in filtered if search_query.lower() in p["filename_base"].lower()]

    st.caption(f"Showing {len(filtered)} of {len(proposals)} generated proposal(s).")

    for p in filtered:
        with st.container(border=True):
            cols = st.columns([3, 2, 2, 2])
            icon = type_icons.get(p["proposal_type"], "🧾")
            cols[0].markdown(f"**{icon} {type_labels.get(p['proposal_type'], p['proposal_type'])}**  \n`{p['filename_base']}`")
            cols[1].caption(f"Generated: {p['generated_at']}")

            with open(p["docx_path"], "rb") as f:
                cols[2].download_button(
                    "📄 DOCX", data=f.read(),
                    file_name=os.path.basename(p["docx_path"]),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"docx_{p['filename_base']}",
                )

            if p["pdf_path"]:
                with open(p["pdf_path"], "rb") as f:
                    cols[3].download_button(
                        "📕 PDF", data=f.read(),
                        file_name=os.path.basename(p["pdf_path"]),
                        mime="application/pdf",
                        key=f"pdf_{p['filename_base']}",
                    )
            else:
                cols[3].caption("PDF unavailable")

render_sidebar_footer()
