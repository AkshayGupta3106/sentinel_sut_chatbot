"""
Metrics tab for the Streamlit dashboard. Recomputes on load (cheap at
this data volume) and renders latency percentiles, error rate/
throughput, and per-stage latency trends as time series.
"""

import pandas as pd
import altair as alt
import streamlit as st
from sqlalchemy import select

from ..trace.db import get_session, init_db
from .metrics_collector import MetricsCollector, DEFAULT_WINDOWS_MINUTES
from .models import MetricPoint


def render_metrics():
    st.subheader("📈 Sentinel AI — Metrics")

    written = MetricsCollector().compute_and_store()
    if written:
        st.caption(f"Recomputed {written} metric points across {len(DEFAULT_WINDOWS_MINUTES)} window sizes.")

    init_db()
    session = get_session()
    try:
        rows = session.execute(select(MetricPoint)).scalars().all()
        df = pd.DataFrame([{
            "window_start": r.window_start,
            "window_minutes": r.window_minutes,
            "metric_name": r.metric_name,
            "value": r.value,
        } for r in rows])
    finally:
        session.close()

    if df.empty:
        st.info("No metrics yet — ask a few questions in the Chat tab first.")
        return

    window_choice = st.selectbox(
        "Window size", sorted(df["window_minutes"].unique()), format_func=lambda m: f"{m} min"
    )
    window_df = df[df["window_minutes"] == window_choice]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Latency percentiles**")
        latency_df = window_df[window_df["metric_name"].str.startswith("latency_")]
        chart = (
            alt.Chart(latency_df)
            .mark_line(point=True)
            .encode(x="window_start:T", y="value:Q", color="metric_name:N",
                    tooltip=["window_start", "metric_name", "value"])
            .properties(height=250)
        )
        st.altair_chart(chart, use_container_width=True)

    with col2:
        st.markdown("**Trace count & error rate**")
        other_df = window_df[window_df["metric_name"].isin(["trace_count", "error_rate_pct"])]
        chart2 = (
            alt.Chart(other_df)
            .mark_line(point=True)
            .encode(x="window_start:T", y="value:Q", color="metric_name:N",
                    tooltip=["window_start", "metric_name", "value"])
            .properties(height=250)
        )
        st.altair_chart(chart2, use_container_width=True)

    st.markdown("**Per-stage avg latency**")
    stage_df = window_df[window_df["metric_name"].str.startswith("stage_latency_avg_ms:")].copy()
    stage_df["stage"] = stage_df["metric_name"].str.replace("stage_latency_avg_ms:", "", regex=False)
    chart3 = (
        alt.Chart(stage_df)
        .mark_line(point=True)
        .encode(x="window_start:T", y="value:Q", color="stage:N",
                tooltip=["window_start", "stage", "value"])
        .properties(height=300)
    )
    st.altair_chart(chart3, use_container_width=True)

    with st.expander("Raw metric points"):
        st.dataframe(window_df.sort_values("window_start"), use_container_width=True, hide_index=True)
