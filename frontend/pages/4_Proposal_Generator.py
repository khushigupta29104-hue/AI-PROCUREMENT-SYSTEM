"""
4_Proposal_Generator.py -- Proposal Generator Page (Core Execution Page)
============================================================================
User selects a proposal type, enters reference numbers (SPR,
Registration, PO, Tender, Remarks) plus any template-specific
user-input fields, then clicks "Generate Proposal".

Two-phase flow so the proposal is EDITABLE before download:
    Phase 1 (Retrieve): runs the AI pipeline (Ollama + ChromaDB) and
        shows live progress (bar, current step, current document,
        elapsed/remaining time, retrieval %, missing fields), then
        displays every field in an EDITABLE form.
    Phase 2 (Finalize & Export): the user reviews/edits field values,
        then clicks "Finalize & Export" to fill the template and
        produce the downloadable DOCX + PDF.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st  # noqa: E402

from backend.core.proposal_manager import get_available_proposal_types, run_export, run_field_resolution  # noqa: E402
from frontend.components.metric_card import render_metric_tiles  # noqa: E402
from frontend.components.progress_tracker import ProgressTracker  # noqa: E402
from frontend.components.proposal_viewer import render_docx_preview  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.status_messages import show_error, show_success  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state, log_activity, reset_generation_state  # noqa: E402
from utils.config_loader import get_field_mapping

st.set_page_config(page_title="Proposal Generator | ProcureAI", page_icon="🧾", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("🧾 Proposal Generator", "Select a template, retrieve fields with AI, review, and export")

proposal_types = get_available_proposal_types()
type_ids = [t["id"] for t in proposal_types]
type_labels = {t["id"]: t["display_name"] for t in proposal_types}
type_icons = {t["id"]: t.get("icon", "🧾") for t in proposal_types}

with st.container(border=True):
    selected_type = st.selectbox(
        "Proposal Type",
        options=type_ids,
        format_func=lambda tid: f"{type_icons[tid]} {type_labels[tid]}",
    )
    if selected_type != st.session_state["selected_proposal_type"]:
        st.session_state["selected_proposal_type"] = selected_type
        reset_generation_state()

    st.markdown("**Reference Numbers** — used to scope the knowledge-base search")
    ref = st.session_state["reference_numbers"]
    c1, c2 = st.columns(2)
    with c1:
        ref["spr_number"] = st.text_input("SPR Number", value=ref.get("spr_number", ""))
        ref["registration_number"] = st.text_input("Registration Number", value=ref.get("registration_number", ""))
        ref["po_number"] = st.text_input("Purchase Order Number", value=ref.get("po_number", ""))
    with c2:
        ref["tender_number"] = st.text_input("Tender Number", value=ref.get("tender_number", ""))
        ref["remarks"] = st.text_area("Additional Remarks", value=ref.get("remarks", ""), height=95)

    mapping = get_field_mapping()["proposal_types"][selected_type]["fields"]
    user_input_fields = [f for f in mapping if f["source"] == "user_input"]
    manual_fields = [f for f in mapping if f["source"] == "manual_user"]

    user_values = st.session_state["user_input_values"]
    if user_input_fields:
        st.markdown(f"**Additional Fields for {type_labels[selected_type]}**")
        for field in user_input_fields:
            key = f"{selected_type}_{field['field_name']}"
            user_values[field["field_name"]] = st.text_input(
                field["field_name"], value=user_values.get(field["field_name"], ""), key=key
            )

    if manual_fields:
        st.caption("Always require manual completion: " + ", ".join(f["field_name"] for f in manual_fields))

    if st.button("🔎 Retrieve & Generate", type="primary"):
        st.session_state["generation_in_progress"] = True
        st.subheader("🔄 AI Generation Progress")
        tracker = ProgressTracker()

        def on_progress(update: dict) -> None:
            tracker.update(update)

        with st.spinner("Running the AI proposal pipeline..."):
            result = run_field_resolution(
                proposal_type_id=selected_type,
                reference_numbers=ref,
                user_input_values=user_values,
                progress_callback=on_progress,
            )

        st.session_state["generation_in_progress"] = False

        if result["success"]:
            st.session_state["resolved_field_values"] = result["field_values"]
            st.session_state["retrieval_report"] = {
                "retrieval_percentage": result["retrieval_percentage"],
                "retrieved_fields": result["retrieved_fields"],
                "missing_fields": result["missing_fields"],
                "manual_fields": result["manual_fields"],
            }
            show_success("Fields retrieved successfully! Review and edit them below before exporting.")
            log_activity(f"Retrieved fields for a {type_labels[selected_type]} proposal")
        else:
            show_error(f"Field retrieval failed: {result['error']}")

# ---- Retrieval report + editable field form ----
resolved = st.session_state.get("resolved_field_values")
report = st.session_state.get("retrieval_report")

if resolved and report:
    st.divider()
    st.subheader("📊 Retrieval Report")
    render_metric_tiles([
        ("📈", f"{report['retrieval_percentage']}%", "Overall Retrieval"),
        ("✅", str(len(report["retrieved_fields"])), "Retrieved Fields"),
        ("⚠️", str(len(report["missing_fields"])), "Missing Fields"),
    ])

    st.divider()
    st.subheader("✏️ Review & Edit Proposal Fields")
    st.caption("Fields marked NA could not be retrieved automatically — edit them here before exporting.")

    with st.form("edit_fields_form"):
        edited_values = {}
        for field_name, value in resolved.items():
            edited_values[field_name] = st.text_input(field_name, value=value)
        submitted = st.form_submit_button("📦 Finalize & Export (DOCX + PDF)", type="primary")

    if submitted:
        with st.spinner("Filling the template and exporting DOCX + PDF..."):
            export_result = run_export(
                proposal_type_id=selected_type,
                field_values=edited_values,
                reference_numbers=st.session_state["reference_numbers"],
            )
        if export_result["success"]:
            st.session_state["last_export_result"] = export_result
            st.session_state["resolved_field_values"] = edited_values
            show_success("Proposal finalized! Scroll down to preview and download.")
            log_activity(f"Exported a {type_labels[selected_type]} proposal")
        else:
            show_error(f"Export failed: {export_result['error']}")

# ---- Preview + downloads ----
export_result = st.session_state.get("last_export_result")
if export_result and export_result.get("success"):
    st.divider()
    st.subheader("👁️ Proposal Preview")
    render_docx_preview(export_result["docx_path"])

    st.divider()
    st.subheader("⬇️ Download")
    d1, d2 = st.columns(2)
    with d1:
        with open(export_result["docx_path"], "rb") as f:
            st.download_button(
                "📄 Download DOCX (opens in MS Word)", data=f.read(),
                file_name=os.path.basename(export_result["docx_path"]),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
            )
    with d2:
        if export_result["pdf_path"] and os.path.exists(export_result["pdf_path"]):
            with open(export_result["pdf_path"], "rb") as f:
                st.download_button(
                    "📕 Download PDF", data=f.read(),
                    file_name=os.path.basename(export_result["pdf_path"]),
                    mime="application/pdf",
                    type="primary",
                )

render_sidebar_footer()
