"""
Section 7 deliverable: run all 3 detection methods against the seeded
metrics and prove they catch the day-8 regression.

Run:
    python -m sentinel.regression.seed_demo_metrics
    python -m sentinel.regression.run_regression
"""

from .regression_engine import RegressionEngine

METRIC_CONFIGS = [
    {"metric_name": "error_rate_pct", "threshold": 10.0, "direction": "above"},
    {"metric_name": "latency_p95_ms", "threshold": 100.0, "direction": "above"},
    {"metric_name": "stage_latency_avg_ms:chromadb_retrieval", "threshold": 50.0, "direction": "above"},
]


def main():
    engine = RegressionEngine(window_minutes=1440)
    flags = engine.run_all(METRIC_CONFIGS)

    if not flags:
        print("No regressions detected.")
        return

    print(f"Detected {len(flags)} regression flag(s):\n")
    for f in sorted(flags, key=lambda x: (x["window_start"], x["metric_name"])):
        print(f"  [{f['severity']:<8}] [{f['method']:<9}] {f['metric_name']}")
        print(f"      {f['description']}")
        print(f"      window_start={f['window_start']}\n")


if __name__ == "__main__":
    main()
