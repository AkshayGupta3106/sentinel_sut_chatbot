"""
Section 5 deliverable: compute and print time-windowed metric rollups.

Run:
    python -m sentinel.metrics.run_metrics
"""

from sqlalchemy import select

from ..trace.db import get_session
from .metrics_collector import MetricsCollector
from .models import MetricPoint


def main():
    collector = MetricsCollector()
    written = collector.compute_and_store()
    print(f"Wrote {written} metric points.\n")

    session = get_session()
    try:
        rows = session.execute(
            select(MetricPoint).order_by(MetricPoint.window_minutes, MetricPoint.window_start, MetricPoint.metric_name)
        ).scalars().all()

        current_window = None
        for r in rows:
            key = (r.window_minutes, r.window_start)
            if key != current_window:
                current_window = key
                print(f"\n--- window={r.window_minutes}min  start={r.window_start} ---")
            print(f"  {r.metric_name:<35} {r.value:.3f}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
