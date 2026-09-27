"""
data_table.py
==============
Thin wrapper around st.dataframe that gives every table in the app
consistent search/sort/filter/pagination behaviour (Streamlit's
dataframe widget natively supports column sorting via header click and
in-browser search via the toolbar's search icon; this helper adds a
text-based pre-filter on top plus consistent styling/height).
"""

from typing import List, Optional

import pandas as pd
import streamlit as st


def render_searchable_table(df: pd.DataFrame, search_columns: Optional[List[str]] = None,
                             search_label: str = "🔍 Search", height: int = 380) -> pd.DataFrame:
    """
    Renders a search box + an interactive, sortable, paginated
    st.dataframe. Returns the (possibly filtered) DataFrame in case the
    caller needs to act on the filtered rows.
    """
    if df.empty:
        st.info("No data available.")
        return df

    query = st.text_input(search_label, "")
    filtered = df
    if query:
        cols = search_columns or df.columns.tolist()
        mask = pd.Series(False, index=df.index)
        for col in cols:
            if col in df.columns:
                mask |= df[col].astype(str).str.contains(query, case=False, na=False)
        filtered = df[mask]

    st.dataframe(filtered, use_container_width=True, hide_index=True, height=height)
    st.caption(f"Showing {len(filtered)} of {len(df)} record(s).")
    return filtered
