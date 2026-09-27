"""
6_Analytics.py -- Analytics Page
===================================
Professional analytics dashboard using Plotly: Document Category
Distribution, Proposal Type Distribution, Monthly Upload Trend,
Knowledge Base Growth, Recent Activity Timeline, and Storage
Utilization. Uses multiple modern colour themes across charts.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd  # noqa: E402
import plotly.express as px  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

from backend.core.analytics_manager import get_full_analytics_snapshot  # noqa: E402
from frontend.components.data_table import render_searchable_table  # noqa: E402
from frontend.components.sidebar import render_sidebar_footer  # noqa: E402
from frontend.components.theme import inject_custom_css, render_hero_banner  # noqa: E402
from frontend.state.session_state import init_session_state  # noqa: E402

st.set_page_config(page_title="Analytics | ProcureAI", page_icon="📊", layout="wide")
inject_custom_css()
init_session_state()

render_hero_banner("📊 Analytics", "Visual insights into your knowledge base and proposal generation activity")

data = get_full_analytics_snapshot()

PALETTE_1 = px.colors.sequential.Purples[::-1]
PALETTE_2 = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#EF4444", "#818CF8"]

row1_a, row1_b = st.columns(2)

with row1_a:
    st.subheader("📚 Document Category Distribution")
    df_cat = pd.DataFrame(data["category_distribution"])
    if df_cat["count"].sum() > 0:
        fig = px.pie(df_cat, names="category", values="count", hole=0.45,
                     color_discrete_sequence=PALETTE_2)
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=340)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Upload documents to see category distribution.")

with row1_b:
    st.subheader("🧾 Proposal Type Distribution")
    df_type = pd.DataFrame(data["proposal_type_distribution"])
    if not df_type.empty:
        fig = px.bar(df_type, x="type", y="count", color="type",
                     color_discrete_sequence=PALETTE_2, text="count")
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=340,
                           xaxis_title="", yaxis_title="Proposals Generated")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Generate proposals to see this chart.")

row2_a, row2_b = st.columns(2)

with row2_a:
    st.subheader("📈 Monthly Upload Trend")
    df_trend = pd.DataFrame(data["monthly_upload_trend"])
    if not df_trend.empty:
        fig = px.line(df_trend, x="month", y="uploads", markers=True,
                       color_discrete_sequence=["#4F46E5"])
        fig.update_traces(line=dict(width=3), fill="tozeroy", fillcolor="rgba(79,70,229,0.12)")
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320,
                           xaxis_title="Month", yaxis_title="Documents Uploaded")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No upload history yet.")

with row2_b:
    st.subheader("🌱 Knowledge Base Growth")
    df_growth = pd.DataFrame(data["kb_growth"])
    if not df_growth.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_growth["month"], y=df_growth["total_documents"],
                                  mode="lines+markers", line=dict(color="#06B6D4", width=3),
                                  fill="tozeroy", fillcolor="rgba(6,182,212,0.15)"))
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320,
                           xaxis_title="Month", yaxis_title="Cumulative Documents")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No growth data yet.")

st.divider()

row3_a, row3_b = st.columns([1.3, 1])

with row3_a:
    st.subheader("💾 Storage Utilization")
    storage = data["storage_utilization"]
    df_storage = pd.DataFrame([{"folder": k, "mb": v} for k, v in storage.items()])
    fig = px.bar(df_storage, x="mb", y="folder", orientation="h", color="folder",
                 color_discrete_sequence=PALETTE_2, text="mb")
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=280,
                       xaxis_title="MB", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with row3_b:
    st.subheader("🕒 Recent Activity Timeline")
    activity_df = pd.DataFrame(data["recent_activity"])
    if not activity_df.empty:
        render_searchable_table(activity_df, search_columns=["event", "detail"], height=280)
    else:
        st.info("No activity recorded yet.")

render_sidebar_footer()
