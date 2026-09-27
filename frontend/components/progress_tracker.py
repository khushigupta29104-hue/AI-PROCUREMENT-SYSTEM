"""
progress_tracker.py
====================
Renders the live generation-progress UI used on the Proposal Generator
page: animated progress bar, current step, current document being
retrieved, elapsed time, estimated remaining time, retrieval
percentage, and missing fields.
"""

import streamlit as st


class ProgressTracker:
    """Holds Streamlit placeholder widgets and updates them live during a generation run."""

    def __init__(self):
        self.bar = st.progress(0, text="Waiting to start...")
        self.step_placeholder = st.empty()
        cols = st.columns(4)
        self.doc_placeholder = cols[0].empty()
        self.elapsed_placeholder = cols[1].empty()
        self.eta_placeholder = cols[2].empty()
        self.retrieval_placeholder = cols[3].empty()
        self.missing_placeholder = st.empty()

    def update(self, info: dict) -> None:
        """
        Args:
            info: dict with 'percent', 'step_label', 'current_document',
                  'elapsed_display', 'eta_display', 'retrieval_percentage',
                  'missing_fields' - exactly the shape produced by
                  services/proposal_generator_service.py's ProgressReporter.
        """
        percent = int(info.get("percent", 0))
        self.bar.progress(min(percent, 100), text=info.get("step_label", ""))
        self.step_placeholder.markdown(f"**Current Step:** {info.get('step_label', '')}")

        self.doc_placeholder.metric("Current Document", info.get("current_document", "-"))
        self.elapsed_placeholder.metric("Elapsed Time", info.get("elapsed_display", "0s"))
        self.eta_placeholder.metric("Est. Remaining", info.get("eta_display", "—"))
        self.retrieval_placeholder.metric("Retrieval %", f"{info.get('retrieval_percentage', 0)}%")

        missing = info.get("missing_fields") or []
        if missing:
            self.missing_placeholder.warning(f"⚠️ Missing fields so far: {', '.join(missing)}")
        else:
            self.missing_placeholder.empty()
