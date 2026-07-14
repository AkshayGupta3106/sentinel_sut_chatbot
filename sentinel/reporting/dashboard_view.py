"""
Reports tab for the Streamlit dashboard: generate the HTML report on
demand, preview it inline, offer a download, and trigger/inspect
Discord alerts.
"""

import io
import os
import zipfile

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy import select
from datetime import date

from ..trace.db import get_session, init_db
from ..repository import SentinelRepository
from ..alerting.models import AlertLog
from ..alerting.discord_bot import (
    send_regression_alert, send_rca_alert, send_daily_digest, DISCORD_WEBHOOK_URL,
)
from ..export.powerbi_export import export_all, EXPORT_DIR
from .html_report import generate_html_report


def render_reports():
    st.subheader("📄 Sentinel AI — Reports & Alerting")

    if not DISCORD_WEBHOOK_URL:
        st.caption(
            "ℹ️ DISCORD_WEBHOOK_URL is not set — alert attempts will be logged as skipped, "
            "not sent. Set the env var locally to test real sends."
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate HTML report"):
            path = generate_html_report(output_path="sentinel_report.html")
            st.session_state["report_path"] = path
            st.success(f"Report generated: {path}")

    with col2:
        if st.button("Send alerts (regressions + RCA + digest)"):
            repo = SentinelRepository()
            sent_r = sum(send_regression_alert(r) for r in repo.get_open_regressions(limit=50))
            sent_rca = sum(send_rca_alert(r) for r in repo.get_rca_reports(limit=50))
            sent_digest = send_daily_digest(repo.get_summary_stats(), reference_id=str(date.today()))
            st.success(
                f"Regression alerts: {sent_r} | RCA alerts: {sent_rca} | "
                f"Digest: {'sent' if sent_digest else 'skipped/duplicate'}"
            )
            st.rerun()

    report_path = st.session_state.get("report_path")
    if report_path:
        with open(report_path) as f:
            html_content = f.read()
        st.download_button("⬇ Download HTML report", html_content, file_name="sentinel_report.html", mime="text/html")
        with st.expander("Preview report"):
            components.html(html_content, height=600, scrolling=True)

    st.divider()
    st.markdown("**Alert log**")
    init_db()
    session = get_session()
    try:
        rows = session.execute(
            select(AlertLog).order_by(AlertLog.sent_at.desc()).limit(50)
        ).scalars().all()
        df = pd.DataFrame([{
            "type": r.alert_type, "reference_id": r.reference_id,
            "success": r.success, "error": r.error, "sent_at": r.sent_at,
        } for r in rows])
    finally:
        session.close()

    if df.empty:
        st.info("No alert attempts yet.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Power BI export")
    st.caption(
        "Power BI Desktop isn't available in this environment, so there's no .pbix file here — "
        "just the real data export and a build guide (docs/POWERBI_GUIDE.md) for building the "
        "actual report yourself in ~20-30 minutes."
    )

    if st.button("Export tables for Power BI"):
        export_all()
        st.success(f"Exported 7 tables (CSV + Parquet) to {EXPORT_DIR}")
        st.rerun()

    if os.path.isdir(EXPORT_DIR) and os.listdir(EXPORT_DIR):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in sorted(os.listdir(EXPORT_DIR)):
                zf.write(os.path.join(EXPORT_DIR, fname), arcname=fname)
        st.download_button(
            "⬇ Download Power BI export (.zip)",
            buffer.getvalue(),
            file_name="sentinel_powerbi_export.zip",
            mime="application/zip",
        )
