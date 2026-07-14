"""
RCA tab for the Streamlit dashboard.
"""

import streamlit as st
from sqlalchemy import select

from ..trace.db import get_session, init_db
from .models import RCAReport
from .rca_engine import RCAEngine

CONFIDENCE_ICON = {"high": "🟢", "medium": "🟡", "low": "🔴"}


def render_rca():
    st.subheader("🔍 Sentinel AI — Root Cause Analysis")
    st.caption(
        "Diagnoses every regressed window from the Regression tab using a rule-based attribution "
        "layer — the rules do the actual reasoning; Gemini (if configured) only rewrites the "
        "finding in plainer English afterward."
    )

    force_refresh = st.checkbox("Force refresh (regenerate reports even if already diagnosed)")
    if st.button("Diagnose all regressed windows"):
        reports = RCAEngine().diagnose_all(force=force_refresh)
        st.success(f"Diagnosed {len(reports)} window(s).")
        st.rerun()

    init_db()
    session = get_session()
    try:
        rows = session.execute(select(RCAReport).order_by(RCAReport.window_start)).scalars().all()
    finally:
        session.close()

    if not rows:
        st.info(
            "No RCA reports yet — seed synthetic history in the Regression tab first, "
            "then click 'Diagnose all regressed windows' above."
        )
        return

    for r in rows:
        icon = CONFIDENCE_ICON.get(r.confidence, "⚪")
        with st.container(border=True):
            st.markdown(f"**{r.window_start}** — `{r.root_cause_category}` {icon} confidence: {r.confidence}")
            st.write(r.summary)
            st.caption(f"Based on {len(r.regression_ids)} regression flag(s), IDs: {r.regression_ids}")
