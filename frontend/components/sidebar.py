"""
sidebar.py
==========
Renders the sidebar footer: project branding, a live (cached) Ollama
connection status pill, and a quick knowledge-base snapshot. Call
render_sidebar_footer() once per page, after inject_custom_css().
"""

import streamlit as st

from llm.ollama_client import health_check
from utils.config_loader import get_system_config


@st.cache_data(ttl=60, show_spinner=False)
def _cached_health_check() -> bool:
    """Caches the Ollama health check for 1 minute (local calls are cheap, but avoids a request on every rerun)."""
    return health_check()


def render_sidebar_footer() -> None:
    with st.sidebar:
        st.divider()
        st.caption("⚙️ AI Procurement Proposal Generation System")

        cfg = get_system_config()
        is_online = _cached_health_check()

        status_class = "online" if is_online else "offline"
        status_text = "Ollama Online" if is_online else "Ollama Offline — run 'ollama serve'"
        st.markdown(
            f'<span class="status-dot {status_class}"></span>'
            f'<span style="font-weight:600;">{status_text}</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"Model: {cfg['ollama']['llm_model']}")
        st.caption(f"Embeddings: local ({cfg['embeddings']['model_name'].split('/')[-1]})")
        st.caption(f"Vector DB: ChromaDB ({cfg['vector_db']['collection_name']})")
