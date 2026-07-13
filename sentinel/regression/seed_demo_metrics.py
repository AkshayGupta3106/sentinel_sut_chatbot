"""
Seeds synthetic daily metrics: 7 stable days followed by a real,
intentional regression on day 8. Real traffic from one test session
collapses into a single time window, which isn't enough to demonstrate
z-score/trend detection -- this is the "synthetic test" the master plan
calls for: deliberately degrade a metric and prove the engine catches it.

Run:
    python -m sentinel.regression.seed_demo_metrics
"""

import random
from datetime import datetime, timedelta

from sqlalchemy import delete

from ..trace.db import get_session, init_db
from ..metrics.models import MetricPoint

SYNTHETIC_METRICS = ["error_rate_pct", "latency_p95_ms", "stage_latency_avg_ms:chromadb_retrieval"]

STABLE_BASELINE = {
    "error_rate_pct": 2.0,
    "latency_p95_ms": 45.0,
    "stage_latency_avg_ms:chromadb_retrieval": 12.0,
}

# Day 8: chromadb_retrieval degrades (simulating e.g. a cold index or a
# bad re-embed), which drags overall latency and error rate up with it.
REGRESSED_VALUES = {
    "error_rate_pct": 34.0,
    "latency_p95_ms": 210.0,
    "stage_latency_avg_ms:chromadb_retrieval": 165.0,
}


def seed(base_day: datetime = datetime(2026, 7, 1)) -> None:
    init_db()
    session = get_session()
    try:
        # Idempotent: clear only the synthetic rows this script owns before reseeding
        session.execute(delete(MetricPoint).where(
            MetricPoint.window_minutes == 1440,
            MetricPoint.metric_name.in_(SYNTHETIC_METRICS),
        ))

        random.seed(42)
        for day in range(7):
            window_start = base_day + timedelta(days=day)
            for metric_name, base_value in STABLE_BASELINE.items():
                noisy_value = base_value * (1 + random.uniform(-0.08, 0.08))
                session.add(MetricPoint(
                    window_start=window_start, window_end=window_start + timedelta(days=1),
                    window_minutes=1440, metric_name=metric_name, value=round(noisy_value, 3),
                ))

        regression_day = base_day + timedelta(days=7)
        for metric_name, value in REGRESSED_VALUES.items():
            session.add(MetricPoint(
                window_start=regression_day, window_end=regression_day + timedelta(days=1),
                window_minutes=1440, metric_name=metric_name, value=value,
            ))

        session.commit()
        print(f"Seeded 7 stable days + 1 regressed day ({regression_day.date()}) for: "
              f"{', '.join(SYNTHETIC_METRICS)}")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
