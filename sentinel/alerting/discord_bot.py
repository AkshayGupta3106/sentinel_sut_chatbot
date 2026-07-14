"""
Discord Alerting.

Webhook-based alerts for new regressions, RCA reports, and a daily
digest. Fails soft exactly like the Gemini calls elsewhere in this
codebase: no webhook URL configured means a clearly logged skip, never
a crash -- and a genuinely unreachable webhook (network error, bad
URL) is caught and logged too, not allowed to take down whatever
triggered the alert.

Deduplication: an AlertLog row is checked BEFORE every send attempt,
keyed by (alert_type, reference_id), so a regression that already got
a successful alert never fires twice -- safe to call this on every
dashboard refresh or every scheduled report run.
"""

import os
from datetime import datetime, timezone

import requests
from sqlalchemy import select

from ..trace.db import get_session, init_db
from .models import AlertLog

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def _already_sent(alert_type: str, reference_id: str) -> bool:
    init_db()
    session = get_session()
    try:
        row = session.execute(
            select(AlertLog).where(
                AlertLog.alert_type == alert_type,
                AlertLog.reference_id == reference_id,
                AlertLog.success == True,  # noqa: E712
            )
        ).scalar_one_or_none()
        return row is not None
    finally:
        session.close()


def _log_attempt(alert_type: str, reference_id: str, success: bool, error: str | None = None) -> None:
    init_db()
    session = get_session()
    try:
        session.add(AlertLog(alert_type=alert_type, reference_id=reference_id, success=success, error=error))
        session.commit()
    finally:
        session.close()


def _send(payload: dict, alert_type: str, reference_id: str) -> bool:
    if _already_sent(alert_type, reference_id):
        return False  # deduplicated -- not an error, just nothing new to send

    if not DISCORD_WEBHOOK_URL:
        _log_attempt(alert_type, reference_id, success=False, error="[SKIPPED] DISCORD_WEBHOOK_URL not set")
        return False

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        _log_attempt(alert_type, reference_id, success=True)
        return True
    except Exception as e:
        _log_attempt(alert_type, reference_id, success=False, error=str(e))
        return False


def send_regression_alert(regression) -> bool:
    color = 0xE74C3C if regression.severity == "critical" else 0xF1C40F
    payload = {
        "embeds": [{
            "title": f"🚨 Regression detected: {regression.metric_name}",
            "description": regression.description,
            "color": color,
            "fields": [
                {"name": "Method", "value": regression.method, "inline": True},
                {"name": "Severity", "value": regression.severity, "inline": True},
                {"name": "Window", "value": str(regression.window_start), "inline": False},
            ],
        }]
    }
    return _send(payload, alert_type="regression", reference_id=str(regression.id))


def send_rca_alert(rca_report) -> bool:
    payload = {
        "embeds": [{
            "title": f"🔍 Root cause: {rca_report.root_cause_category}",
            "description": rca_report.summary[:2000],
            "color": 0x3498DB,
            "fields": [
                {"name": "Confidence", "value": rca_report.confidence, "inline": True},
                {"name": "Window", "value": str(rca_report.window_start), "inline": True},
            ],
        }]
    }
    return _send(payload, alert_type="rca", reference_id=str(rca_report.id))


def send_daily_digest(stats: dict, reference_id: str) -> bool:
    payload = {
        "embeds": [{
            "title": "📊 Sentinel AI — Daily Digest",
            "color": 0x2ECC71,
            "fields": [{"name": k, "value": str(v), "inline": True} for k, v in stats.items()],
        }]
    }
    return _send(payload, alert_type="digest", reference_id=reference_id)
