"""
session_state.py
=================
Centralizes Streamlit session_state initialization and helpers so
pages don't scatter raw st.session_state[...] keys everywhere.
"""

import datetime

import streamlit as st

DEFAULTS = {
    "selected_proposal_type": None,
    "reference_numbers": {
        "spr_number": "", "registration_number": "", "po_number": "",
        "tender_number": "", "remarks": "",
    },
    "user_input_values": {},
    "resolved_field_values": None,   # phase-1 (retrieval) result, editable in the UI
    "retrieval_report": None,        # {"retrieval_percentage", "retrieved_fields", "missing_fields", "manual_fields"}
    "last_export_result": None,      # phase-2 (docx/pdf export) result
    "generation_in_progress": False,
    "recent_activity": [],
}


def init_session_state() -> None:
    """Ensures every key in DEFAULTS exists in st.session_state (idempotent)."""
    for key, default_value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = (
                dict(default_value) if isinstance(default_value, dict)
                else list(default_value) if isinstance(default_value, list)
                else default_value
            )


def log_activity(message: str) -> None:
    """Appends a short entry to the 'Recent Activity' feed shown on the Dashboard."""
    init_session_state()
    entry = f"{datetime.datetime.now().strftime('%H:%M:%S')} — {message}"
    st.session_state["recent_activity"].insert(0, entry)
    st.session_state["recent_activity"] = st.session_state["recent_activity"][:10]


def reset_generation_state() -> None:
    """Clears the in-progress generation state (called when the user picks a new proposal type)."""
    st.session_state["resolved_field_values"] = None
    st.session_state["retrieval_report"] = None
    st.session_state["last_export_result"] = None
