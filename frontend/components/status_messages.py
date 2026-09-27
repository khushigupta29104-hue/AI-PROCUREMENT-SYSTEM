"""
status_messages.py
===================
Standardized success/warning/error/info banner helpers so every page
shows consistent, styled feedback (uses style.css's alert border-accent).
"""

import streamlit as st


def show_success(message: str) -> None:
    st.success(f"✅ {message}")


def show_error(message: str) -> None:
    st.error(f"❌ {message}")


def show_warning(message: str) -> None:
    st.warning(f"⚠️ {message}")


def show_info(message: str) -> None:
    st.info(f"ℹ️ {message}")
