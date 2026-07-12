"""
Metrics Collector.

Rolls individual traces/trace_events up into time-windowed aggregates:
p50/p95/p99 trace latency, error rate, throughput, and per-stage avg
latency. This is what turns "a pile of traces" into the kind of
time-series data Section 7 (Regression Detection) actually needs --
you can't detect a regression by staring at one trace at a time.

Honest scope note: real observability platforms also roll up cost
(tokens spent, $ spent) and quality scores (faithfulness, relevance)
per window. Cost tracking needs real Gemini token usage data, and
quality scores need the Evaluation Engine -- both come in Section 6+.
This section only has latency/error/throughput to work with, which is
already true and useful, not padded with numbers we can't back up yet.
"""

import math
from datetime import datetime, timedelta, timezone

import pandas as pd
from sqlalchemy import select, delete

from ..trace.db import get_session, init_db
from ..trace.models import Trace, TraceEvent
from .models import MetricPoint

DEFAULT_WINDOWS_MINUTES = [5, 60, 1440]  # 5-min, 1-hour, 1-day rollups


def _floor_to_window(ts: datetime, window_minutes: int) -> datetime:
    """
    Buckets a timestamp down to the start of its window.

    Normalizes to naive UTC first: SQLite doesn't actually preserve
    timezone-awareness on round-trip (a well-known SQLAlchemy+SQLite
    quirk), so a timestamp written as tz-aware comes back naive when
    read from the DB. Comparing naive vs aware datetimes raises
    TypeError, so we strip tzinfo consistently on the way in.
    """
    if ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)
    epoch = datetime(1970, 1, 1)
    minutes_since_epoch = (ts - epoch).total_seconds() / 60
    floored = math.floor(minutes_since_epoch / window_minutes) * window_minutes
    return epoch + timedelta(minutes=floored)


def _percentile(series: pd.Series, q: float) -> float:
    if series.empty:
        return 0.0
    return float(series.quantile(q))


class MetricsCollector:
    """
    Idempotent per (window_start, window_minutes): recomputing simply
    replaces existing rows for that window rather than duplicating
    them. Safe to run repeatedly -- in a real deployment this would be
    a scheduled job (cron / APScheduler) firing every few minutes as
    new traces land.
    """

    def __init__(self, window_minutes_list: list[int] | None = None):
        self.window_minutes_list = window_minutes_list or DEFAULT_WINDOWS_MINUTES

    def compute_and_store(self) -> int:
        init_db()
        session = get_session()
        try:
            traces = session.execute(select(Trace)).scalars().all()
            events = session.execute(select(TraceEvent)).scalars().all()

            if not traces:
                return 0

            traces_df = pd.DataFrame([{
                "trace_id": t.trace_id,
                "started_at": t.started_at,
                "total_latency_ms": t.total_latency_ms,
                "has_error": t.has_error,
            } for t in traces])

            events_df = pd.DataFrame([{
                "trace_id": e.trace_id,
                "stage_name": e.stage_name,
                "latency_ms": e.latency_ms,
            } for e in events])

            total_written = 0
            for window_minutes in self.window_minutes_list:
                total_written += self._compute_for_window(session, traces_df, events_df, window_minutes)

            session.commit()
            return total_written
        finally:
            session.close()

    def _compute_for_window(self, session, traces_df, events_df, window_minutes: int) -> int:
        traces_df = traces_df.copy()
        traces_df["window_start"] = traces_df["started_at"].apply(
            lambda ts: _floor_to_window(ts, window_minutes)
        )
        events_df = events_df.merge(traces_df[["trace_id", "window_start"]], on="trace_id", how="left")

        written = 0
        for window_start, group in traces_df.groupby("window_start"):
            window_end = window_start + timedelta(minutes=window_minutes)

            metrics = {
                "trace_count": float(len(group)),
                "error_rate_pct": float((group["has_error"].sum() / len(group)) * 100),
                "latency_p50_ms": _percentile(group["total_latency_ms"], 0.50),
                "latency_p95_ms": _percentile(group["total_latency_ms"], 0.95),
                "latency_p99_ms": _percentile(group["total_latency_ms"], 0.99),
            }

            stage_group = events_df[events_df["window_start"] == window_start]
            for stage_name, stage_rows in stage_group.groupby("stage_name"):
                metrics[f"stage_latency_avg_ms:{stage_name}"] = float(stage_rows["latency_ms"].mean())

            # Replace, don't append -- keeps recompute idempotent
            session.execute(
                delete(MetricPoint).where(
                    MetricPoint.window_start == window_start,
                    MetricPoint.window_minutes == window_minutes,
                )
            )

            for metric_name, value in metrics.items():
                session.add(MetricPoint(
                    window_start=window_start,
                    window_end=window_end,
                    window_minutes=window_minutes,
                    metric_name=metric_name,
                    value=value,
                ))
                written += 1

        return written
