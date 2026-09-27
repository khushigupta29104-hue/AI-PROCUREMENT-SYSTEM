"""
7_Settings.py -- Settings Page
=================================
Lets an admin view and edit key system settings (Ollama host/model,
temperature, chunking parameters, retrieval top_k, file upload limits)
persisted to config/system_config.json. Changes apply immediately
(config cache cleared on save) without restarting Streamlit. Confirms
embeddings run locally too (no key needed anywhere in this system).
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.status_messages import show_info, show_success  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402
from llm.ollama_client import health_check  # noqa: E402
from utils.config_loader import clear_config_cache, get_system_config, resolve_path

st.set_page_config(page_title="Settings | ProcureAI", page_icon="⚙️", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("⚙️ Settings", "Configure the local Ollama model, retrieval behaviour, and upload limits")

cfg = get_system_config()

st.subheader("🤖 Ollama Configuration (Local — no API key required)")
show_info("This system runs entirely on your machine. No API key, no internet dependency, no usage quota. "
          "Make sure Ollama is installed and running (`ollama serve`), and the model below has been pulled "
          "(`ollama pull <model_name>`).")
st.caption(f"Connection status: {'🟢 Online' if health_check() else '🔴 Offline — run \"ollama serve\"'}")

c1, c2 = st.columns(2)
host = c1.text_input("Ollama Host", value=cfg["ollama"]["host"])
llm_model = c2.text_input("LLM Model", value=cfg["ollama"]["llm_model"])
temperature = c1.slider("Temperature", 0.0, 1.0, float(cfg["ollama"]["temperature"]), 0.05)
max_tokens = c2.number_input("Max Output Tokens", min_value=128, max_value=8192, value=int(cfg["ollama"]["max_output_tokens"]), step=64)
timeout = c1.number_input("Request Timeout (seconds)", min_value=10, max_value=600, value=int(cfg["ollama"]["request_timeout_seconds"]), step=10)

st.divider()
st.subheader("🧠 Embeddings (Local — no API key required)")
show_info(f"Embeddings run fully locally via `{cfg['embeddings']['model_name']}` (CPU, sentence-transformers). "
          f"No API key, no quota, no internet required after the first model download.")

st.divider()
st.subheader("🧩 Chunking & Retrieval")
c3, c4 = st.columns(2)
chunk_size = c3.number_input("Chunk Size", min_value=200, max_value=4000, value=int(cfg["chunking"]["chunk_size"]), step=50)
chunk_overlap = c4.number_input("Chunk Overlap", min_value=0, max_value=1000, value=int(cfg["chunking"]["chunk_overlap"]), step=10)
top_k = c3.number_input("Retrieval Top-K", min_value=1, max_value=20, value=int(cfg["retrieval"]["top_k"]), step=1)

st.divider()
st.subheader("📁 File Upload Limits")
u1, u2 = st.columns(2)
max_size = u1.number_input("Max File Size (MB)", min_value=1, max_value=200, value=int(cfg["file_upload"]["max_file_size_mb"]), step=1)
max_files = u2.number_input("Soft Limit: Files per Upload Batch", min_value=1, max_value=500, value=int(cfg["file_upload"]["max_files_per_upload"]), step=5)

if st.button("💾 Save Settings", type="primary"):
    cfg["ollama"]["host"] = host
    cfg["ollama"]["llm_model"] = llm_model
    cfg["ollama"]["temperature"] = temperature
    cfg["ollama"]["max_output_tokens"] = int(max_tokens)
    cfg["ollama"]["request_timeout_seconds"] = int(timeout)
    cfg["chunking"]["chunk_size"] = int(chunk_size)
    cfg["chunking"]["chunk_overlap"] = int(chunk_overlap)
    cfg["retrieval"]["top_k"] = int(top_k)
    cfg["file_upload"]["max_file_size_mb"] = int(max_size)
    cfg["file_upload"]["max_files_per_upload"] = int(max_files)

    config_path = resolve_path("config", "system_config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    clear_config_cache()
    show_success("Settings saved. Changes apply immediately (no restart required).")

render_sidebar_footer()
