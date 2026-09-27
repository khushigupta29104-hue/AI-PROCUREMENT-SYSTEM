"""
9_About.py -- About Page
===========================
Static informational page: project description, tech stack, pipeline
overview, and supported proposal types / document categories.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from backend.core.proposal_manager import get_available_proposal_types  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402
from utils.config_loader import get_system_config

st.set_page_config(page_title="About | ProcureAI", page_icon="ℹ️", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("ℹ️ About This System", "A B.Tech final-year AI project built to enterprise standards")

st.markdown(
    """
The **AI Procurement Proposal Generation System** automatically drafts
procurement proposals by retrieving facts from your organisation's own
documents (SPR, Registration, Purchase Order, Tender, and Vendor
files) using a Retrieval-Augmented Generation (RAG) pipeline powered by
**Ollama**, running entirely on your own machine (no API key, no internet dependency, no usage quota).
"""
)

st.subheader("🧱 Technology Stack")
st.markdown(
    """
| Layer | Technology |
|---|---|
| Frontend | Streamlit (custom enterprise CSS theme) |
| Backend | Python (modular architecture) |
| LLM | Ollama (local, Llama 3.1 8B) |
| Orchestration | LangChain |
| Vector Database | ChromaDB |
| Embeddings | Local HuggingFace sentence-transformers (no API key) |
| PDF Reading | PyMuPDF (`fitz`) |
| DOCX Reading/Writing | `python-docx` |
| PDF Export | ReportLab |
| Data Processing | Pandas |
| Charts | Plotly |
| OCR | None (not used, by design) |
"""
)

st.subheader("🔄 AI Pipeline")
st.markdown(
    """
```
Upload Documents → Knowledge Base → Text Extraction → Chunking →
Embeddings (local) → ChromaDB → LangChain Retrieval → Ollama (local) →
Retrieve Required Fields → Fill Proposal Template →
Generate Proposal → Preview → Download DOCX / PDF
```
"""
)

st.subheader("📑 Supported Proposal Types")
for t in get_available_proposal_types():
    st.markdown(f"- **{t.get('icon','🧾')} {t['display_name']}** — {t['description']}")

st.subheader("🗂️ Knowledge Base Categories")
cfg = get_system_config()
for cat in cfg["knowledge_base_categories"]:
    icon = cfg["knowledge_base_category_icons"].get(cat, "📄")
    st.markdown(f"- {icon} {cfg['knowledge_base_category_labels'].get(cat, cat)}")

st.divider()
st.caption("Built as a clean, modular, enterprise-style reference architecture — new proposal types, document types, and fields can be added purely via configuration files, with no core code changes.")

render_sidebar_footer()
