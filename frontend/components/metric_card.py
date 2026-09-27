"""
metric_card.py
================
Renders custom KPI "metric tiles" (icon + big number + label) styled
via the .metric-tile CSS class, used on the Dashboard and Analytics
pages instead of Streamlit's plain st.metric for a more premium look.
"""

from typing import List, Tuple

import streamlit as st


def render_metric_tiles(tiles: List[Tuple[str, str, str]]) -> None:
    """
    Renders a row of metric tiles.

    Args:
        tiles: list of (icon_emoji, value, label) tuples, e.g.
               [("📄", "24", "Total Documents"), ...]
    """
    cols = st.columns(len(tiles))
    for col, (icon, value, label) in zip(cols, tiles):
        with col:
            st.markdown(
                f"""
                <div class="metric-tile">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_badge(text: str, kind: str = "info") -> str:
    """Returns an HTML badge span (kind: success/danger/warning/info) for inline use inside st.markdown(...)."""
    return f'<span class="badge badge-{kind}">{text}</span>'
