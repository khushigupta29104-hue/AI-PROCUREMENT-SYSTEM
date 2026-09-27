"""
1_Dashboard.py -- Home Dashboard Page
========================================
Displays: Total Documents, Knowledge Base Status, Templates Available,
Generated Proposals, Today's Uploads, Storage Used, Recent Activities,
Quick Actions, Recent Generated Proposals, System Status.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from backend.core.analytics_manager import get_todays_uploads, get_total_storage_mb  # noqa: E402
from backend.core.knowledge_base_manager import get_kb_stats  # noqa: E402
from backend.core.proposal_manager import get_available_proposal_types, list_generated_proposals  # noqa: E402
from frontend.components.metric_card import render_badge, render_metric_tiles  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402
from llm.ollama_client import health_check  # noqa: E402

st.set_page_config(page_title="Dashboard | ProcureAI", page_icon="🏠", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("🏠 Dashboard", "Live overview of your knowledge base, templates, and generated proposals")

kb_stats = get_kb_stats()
proposal_types = get_available_proposal_types()
generated = list_generated_proposals()
api_status = "🟢 Online" if health_check() else "🔴 Offline"

render_metric_tiles([
    ("📚", str(kb_stats["total_documents"]), "Total Documents"),
    ("🧩", str(len(proposal_types)), "Templates Available"),
    ("🧾", str(len(generated)), "Generated Proposals"),
    ("🆕", str(get_todays_uploads()), "Today's Uploads"),
])

st.write("")

render_metric_tiles([
    ("💾", f"{get_total_storage_mb()} MB", "Storage Used"),
    ("🔗", str(kb_stats["total_vectors"]), "Indexed Chunks (ChromaDB)"),
    ("🤖", api_status, "System Status"),
    ("⏱️", kb_stats["last_checked"].split(" ")[1], "Last Checked"),
])

st.divider()

col_kb, col_activity = st.columns([1.3, 1])

with col_kb:
    st.subheader("📚 Knowledge Base Status")
    with st.container(border=True):
        for cat in kb_stats["categories"]:
            label = kb_stats["labels"].get(cat, cat)
            icon = kb_stats["icons"].get(cat, "📄")
            count = kb_stats["document_counts"].get(cat, 0)
            badge = render_badge(f"{count} docs", "info" if count else "warning")
            st.markdown(f"**{icon} {label}** &nbsp; {badge}", unsafe_allow_html=True)

with col_activity:
    st.subheader("🕒 Recent Activity")
    with st.container(border=True):
        activity = st.session_state.get("recent_activity", [])
        if activity:
            for entry in activity:
                st.write(f"- {entry}")
        else:
            st.caption("No activity yet this session.")

st.divider()

st.subheader("⚡ Quick Actions")
qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    st.page_link("pages/2_Upload_Documents.py", label="📤 Upload Documents", icon="📤")
with qa2:
    st.page_link("pages/4_Proposal_Generator.py", label="🧾 Generate a Proposal", icon="🧾")
with qa3:
    st.page_link("pages/5_Generated_Proposals.py", label="⬇️ Download Proposals", icon="⬇️")
with qa4:
    st.page_link("pages/6_Analytics.py", label="📊 View Analytics", icon="📊")

st.divider()

st.subheader("🧾 Recent Generated Proposals")
type_labels = {t["id"]: t["display_name"] for t in proposal_types}
if generated:
    for p in generated[:5]:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{type_labels.get(p['proposal_type'], p['proposal_type'])}** &nbsp; `{p['filename_base']}`")
            c2.caption(p["generated_at"])
else:
    st.caption("No proposals generated yet — head to Proposal Generator to create your first one.")

render_sidebar_footer()
