"""
Regression Detection Engine.

Operates on the metrics_timeseries table Section 5 built -- not on raw
traces. Three detection methods, each catching a different failure
pattern:

  - Threshold: a hard business rule ("error rate must never exceed
    10%"), independent of history. Cheap and obvious, but blind to
    gradual decay that never crosses the line.
  - Z-score: flags a window that's a statistical outlier relative to
    a rolling baseline (mean + stdev of prior windows). Catches sudden
    jumps a fixed threshold might not be tuned to catch.
  - Trend: flags a sustained decline across several consecutive
    windows, even if no single window looks alarming on its own --
    catches slow degradation the other two both miss.
"""

import statistics
from datetime import datetime

from sqlalchemy import select

from ..trace.db import get_session, init_db
from ..metrics.models import MetricPoint
from .models import Regression


class RegressionEngine:
    def __init__(self, window_minutes: int = 1440):
        self.window_minutes = window_minutes

    def _get_series(self, session, metric_name: str) -> list[tuple[datetime, float]]:
        rows = session.execute(
            select(MetricPoint)
            .where(MetricPoint.metric_name == metric_name, MetricPoint.window_minutes == self.window_minutes)
            .order_by(MetricPoint.window_start)
        ).scalars().all()
        return [(r.window_start, r.value) for r in rows]

    def detect_threshold(self, metric_name: str, threshold: float, direction: str = "above") -> list[dict]:
        session = get_session()
        try:
            series = self._get_series(session, metric_name)
            flags = []
            for window_start, value in series:
                breached = (value > threshold) if direction == "above" else (value < threshold)
                if breached:
                    flags.append({
                        "metric_name": metric_name, "method": "threshold",
                        "window_start": window_start, "current_value": value,
                        "baseline_value": threshold, "delta_pct": None,
                        "severity": "critical",
                        "description": f"{metric_name}={value:.2f} breached fixed threshold {threshold} ({direction}).",
                    })
            return flags
        finally:
            session.close()

    def detect_zscore(self, metric_name: str, z_thresh: float = 2.0, min_baseline_points: int = 3) -> list[dict]:
        session = get_session()
        try:
            series = self._get_series(session, metric_name)
            flags = []
            for i in range(min_baseline_points, len(series)):
                baseline = [v for _, v in series[:i]]
                window_start, current = series[i]
                mean = statistics.mean(baseline)
                stdev = statistics.pstdev(baseline) if len(baseline) > 1 else 0
                if stdev == 0:
                    continue
                z = (current - mean) / stdev
                if abs(z) >= z_thresh:
                    delta_pct = ((current - mean) / mean * 100) if mean != 0 else None
                    flags.append({
                        "metric_name": metric_name, "method": "zscore",
                        "window_start": window_start, "current_value": current,
                        "baseline_value": mean, "delta_pct": delta_pct,
                        "severity": "critical" if abs(z) >= 3 else "warning",
                        "description": f"{metric_name}={current:.2f} is {z:.2f} std devs from baseline mean {mean:.2f}.",
                    })
            return flags
        finally:
            session.close()

    def detect_trend(self, metric_name: str, lookback: int = 5, min_change_pct: float = 10.0) -> list[dict]:
        """Flags a sustained move across the last `lookback` windows even
        if no single window crosses a threshold or looks like an outlier."""
        session = get_session()
        try:
            series = self._get_series(session, metric_name)
            if len(series) < lookback:
                return []
            recent = series[-lookback:]
            first_val, last_val = recent[0][1], recent[-1][1]
            if first_val == 0:
                return []
            pct_change = (last_val - first_val) / first_val * 100
            if abs(pct_change) < min_change_pct:
                return []
            return [{
                "metric_name": metric_name, "method": "trend",
                "window_start": recent[-1][0], "current_value": last_val,
                "baseline_value": first_val, "delta_pct": pct_change,
                "severity": "warning",
                "description": f"{metric_name} moved {pct_change:+.1f}% over the last {lookback} windows "
                                f"({first_val:.2f} -> {last_val:.2f}).",
            }]
        finally:
            session.close()

    def persist(self, flags: list[dict]) -> int:
        init_db()
        session = get_session()
        written = 0
        try:
            for f in flags:
                exists = session.execute(
                    select(Regression).where(
                        Regression.metric_name == f["metric_name"],
                        Regression.method == f["method"],
                        Regression.window_start == f["window_start"],
                    )
                ).scalar_one_or_none()
                if exists:
                    continue
                session.add(Regression(
                    metric_name=f["metric_name"], method=f["method"], severity=f["severity"],
                    window_start=f["window_start"], window_minutes=self.window_minutes,
                    baseline_value=f["baseline_value"], current_value=f["current_value"],
                    delta_pct=f["delta_pct"], description=f["description"],
                ))
                written += 1
            session.commit()
            return written
        finally:
            session.close()

    def run_all(self, metric_configs: list[dict]) -> list[dict]:
        """
        metric_configs: [{"metric_name": ..., "threshold": ..., "direction": "above"|"below"}, ...]
        Threshold checks use the given config; z-score and trend run on
        every listed metric_name regardless of the threshold value.
        """
        all_flags = []
        for cfg in metric_configs:
            all_flags.extend(self.detect_threshold(cfg["metric_name"], cfg["threshold"], cfg.get("direction", "above")))
        for name in {c["metric_name"] for c in metric_configs}:
            all_flags.extend(self.detect_zscore(name))
            all_flags.extend(self.detect_trend(name))

        self.persist(all_flags)
        return all_flags
