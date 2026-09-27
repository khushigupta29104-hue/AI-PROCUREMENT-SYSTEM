"""
theme.py
=========
Loads frontend/assets/style.css and injects it into the page via
st.markdown(unsafe_allow_html=True). Call inject_custom_css() once at
the top of every page (right after st.set_page_config) to apply the
enterprise glassmorphism theme consistently across the whole dashboard.
"""

import os

import streamlit as st

from utils.config_loader import resolve_path

_CSS_PATH = resolve_path("frontend", "assets", "style.css")


@st.cache_data(show_spinner=False)
def _read_css() -> str:
    with open(_CSS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def inject_custom_css() -> None:
    """Injects the project's dedicated style.css into the current Streamlit page."""
    css = _read_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_hero_banner(title: str, subtitle: str) -> None:
    """Renders the gradient hero banner used at the top of most pages."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
