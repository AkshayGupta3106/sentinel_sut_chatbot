"""
Regression tab for the Streamlit dashboard. Seeds synthetic daily
history on demand (real traffic from one test session doesn't produce
enough time-series spread to demonstrate detection), runs all 3
detection methods, and shows the metric charts alongside flagged
regressions.
"""

import pandas as pd
import altair as alt
import streamlit as st
from sqlalchemy import select

from ..trace.db import get_session, init_db
from ..metrics.models import MetricPoint
from .models import Regression
from .regression_engine import RegressionEngine
from .seed_demo_metrics import seed, SYNTHETIC_METRICS

METRIC_CONFIGS = [
    {"metric_name": "error_rate_pct", "threshold": 10.0, "direction": "above"},
    {"metric_name": "latency_p95_ms", "threshold": 100.0, "direction": "above"},
    {"metric_name": "stage_latency_avg_ms:chromadb_retrieval", "threshold": 50.0, "direction": "above"},
]


def render_regression():
    st.subheader("🚨 Sentinel AI — Regression Detection")
    st.caption(
        "Runs against seeded synthetic daily metrics (7 stable days + 1 injected regression) — "
        "a single test session doesn't produce enough real time-series spread to demonstrate "
        "trend/z-score detection, so this deliberately injects one, as the design doc calls for."
    )

    if st.button("Seed synthetic history + run detection"):
        seed()
        flags = RegressionEngine(window_minutes=1440).run_all(METRIC_CONFIGS)
        st.success(f"Seeded synthetic metrics and detected {len(flags)} regression flag(s).")
        st.rerun()

    init_db()
    session = get_session()
    try:
        metric_rows = session.execute(
            select(MetricPoint).where(
                MetricPoint.window_minutes == 1440,
                MetricPoint.metric_name.in_(SYNTHETIC_METRICS),
            )
        ).scalars().all()
        regression_rows = session.execute(select(Regression).order_by(Regression.window_start)).scalars().all()
    finally:
        session.close()

    if not metric_rows:
        st.info("No synthetic history yet — click the button above to seed it.")
        return

    metrics_df = pd.DataFrame([{
        "window_start": r.window_start, "metric_name": r.metric_name, "value": r.value,
    } for r in metric_rows])

    flagged_starts = {r.window_start for r in regression_rows}

    for metric_name in SYNTHETIC_METRICS:
        sub = metrics_df[metrics_df["metric_name"] == metric_name].copy()
        sub["flagged"] = sub["window_start"].isin(flagged_starts)
        st.markdown(f"**{metric_name}**")
        line = alt.Chart(sub).mark_line(point=True).encode(
            x="window_start:T", y="value:Q",
            color=alt.Color("flagged:N", scale=alt.Scale(domain=[False, True], range=["#4c78a8", "#e74c3c"])),
            tooltip=["window_start", "value", "flagged"],
        ).properties(height=180)
        st.altair_chart(line, use_container_width=True)

    st.divider()
    st.markdown("**Detected regressions**")
    if not regression_rows:
        st.info("No regressions flagged yet.")
        return

    reg_df = pd.DataFrame([{
        "metric_name": r.metric_name, "method": r.method, "severity": r.severity,
        "window_start": r.window_start, "baseline": r.baseline_value,
        "current": r.current_value, "delta_pct": r.delta_pct, "description": r.description,
    } for r in regression_rows])
    st.dataframe(reg_df, use_container_width=True, hide_index=True)
