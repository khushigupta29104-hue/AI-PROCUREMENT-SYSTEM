"""
app.py -- Streamlit Main Entrypoint
=====================================
Root Streamlit application file. Run with:

    streamlit run frontend/app.py

Sets the global page config, applies the custom enterprise theme
(style.css), and initializes session_state. No API key or .env file
is required anywhere in this system -- the LLM (Ollama) and the
embedding model both run entirely on your own machine.

Streamlit's multipage-app mechanism automatically turns every file
under frontend/pages/ into a sidebar navigation entry (ordered by
numeric filename prefix).
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402

st.set_page_config(
    page_title="AI Procurement Proposal Generation System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
init_session_state()

render_hero_banner(
    "📄 AI Procurement Proposal Generation System",
    "Enterprise-grade, RAG-powered proposal generation using local Ollama + LangChain + ChromaDB",
)

st.info("👈 Use the sidebar to navigate: Dashboard, Upload Documents, Knowledge Base, Proposal Generator, Generated Proposals, Analytics, Settings, Help, About.")
st.caption("🔒 Fully local: no API key required. Make sure Ollama is running (`ollama serve`) before generating proposals.")

render_sidebar_footer()

st.markdown('<div class="app-footer">AI Procurement Proposal Generation System — B.Tech Final Year Project</div>', unsafe_allow_html=True)
