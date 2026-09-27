"""
proposal_viewer.py
===================
Renders a read-only preview of a generated .docx proposal's content
(paragraphs + tables) inside Streamlit.
"""

import streamlit as st
from docx import Document


def render_docx_preview(docx_path: str) -> None:
    """Displays the paragraphs and tables of a .docx file as native Streamlit elements."""
    document = Document(docx_path)

    for element in document.element.body.iterchildren():
        tag = element.tag.rsplit("}", 1)[-1]

        if tag == "p":
            text = "".join(node.text or "" for node in element.iter() if node.tag.endswith("}t")).strip()
            if text:
                st.markdown(text)

        elif tag == "tbl":
            for table in document.tables:
                if table._tbl is element:
                    rows = [[cell.text for cell in row.cells] for row in table.rows]
                    if rows:
                        st.table(rows)
                    break
