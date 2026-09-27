"""
8_Help.py -- Help Page
==========================
Step-by-step usage guide (FAQ style) covering: setting up Ollama (local AI)
key, uploading documents, generating a proposal, editing before
download, and troubleshooting common errors.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402

st.set_page_config(page_title="Help | ProcureAI", page_icon="❓", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("❓ Help & FAQ", "Everything you need to get the system running and generating proposals")

with st.expander("🖥️ How do I set up Ollama (the local AI engine)?", expanded=True):
    st.markdown(
        "1. Download and install Ollama from [ollama.com/download](https://ollama.com/download).\n"
        "2. Restart your computer once after installing (ensures Ollama is on your system PATH).\n"
        "3. Pull the two required models (one-time, needs internet):\n"
        "```\nollama pull llama3.1:8b\n```\n"
        "4. Start the Ollama server (keep this terminal open while using the app):\n"
        "```\nollama serve\n```\n"
        "5. In a separate terminal, run the Streamlit app as usual (`streamlit run frontend/app.py`).\n\n"
        "No API key, no account, no internet needed after the models are pulled — everything "
        "runs on your own machine."
    )

with st.expander("📤 How do I add documents to the Knowledge Base?"):
    st.markdown(
        "Go to **Upload Documents**, choose the correct category (SPR, Registration, Purchase Order, "
        "Tender, or Vendor), and drag & drop your PDF/DOCX files. You can upload as many as you like — "
        "there's no hard limit. Documents are automatically text-extracted, chunked, embedded, and "
        "added to ChromaDB — ready to use immediately."
    )

with st.expander("🧾 How do I generate a proposal?"):
    st.markdown(
        "1. Go to **Proposal Generator**.\n"
        "2. Select a proposal type (Honeywell, Dassault, Common Vendor, Foreign Vendor, or General Notice).\n"
        "3. Enter the relevant reference numbers (SPR, Registration, PO, Tender) — these scope the AI's search.\n"
        "4. Click **Retrieve & Generate**. Watch the live progress bar as the AI reads your documents.\n"
        "5. Review the retrieved fields in the editable form — fix any field marked `NA`.\n"
        "6. Click **Finalize & Export** to produce the final DOCX and PDF.\n"
        "7. Preview it, then use **Download DOCX** or **Download PDF**."
    )

with st.expander("✏️ Can I edit the proposal before downloading?"):
    st.markdown(
        "Yes. After field retrieval, every field appears in an editable form on the Proposal Generator "
        "page. Edit any value (including fields marked `NA`) before clicking **Finalize & Export** — "
        "your edits are what gets written into the final document."
    )

with st.expander("📄 Will the downloaded DOCX open in Microsoft Word?"):
    st.markdown(
        "Yes. The file is a standard Word `.docx` (OpenXML WordprocessingML) file. Once downloaded, "
        "your operating system will open it with whichever application is set as the default handler "
        "for `.docx` files — normally Microsoft Word."
    )

with st.expander("⚠️ Troubleshooting: 'Ollama Offline'"):
    st.markdown(
        "- Make sure the Ollama server is running: open a terminal and run `ollama serve` "
        "(leave it running in the background).\n"
        "- Confirm the model has been pulled: run `ollama list` and check `llama3.1:8b` appears. "
        "If not, run `ollama pull llama3.1:8b`.\n"
        "- If Ollama was just installed, restart your computer once so it's on your system PATH.\n"
        "- Document indexing/search still works even if Ollama is offline (embeddings run locally); "
        "only the Proposal Generator's field-extraction step needs Ollama running."
    )

with st.expander("⚠️ Troubleshooting: A field always shows 'NA'"):
    st.markdown(
        "- Make sure the relevant source document (e.g. the Purchase Order) has actually been uploaded "
        "to the correct category in the Knowledge Base.\n"
        "- Try re-uploading with a clearer reference number in the Proposal Generator form so the search "
        "can find the right document.\n"
        "- You can always fix the value manually in the editable field form before exporting."
    )

render_sidebar_footer()
