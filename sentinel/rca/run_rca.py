"""
Section 8 deliverable: diagnose every window Section 7 flagged and
print the root cause report.

Run (after Section 7's seed + detect):
    python -m sentinel.regression.seed_demo_metrics
    python -m sentinel.regression.run_regression
    python -m sentinel.rca.run_rca
"""

from .rca_engine import RCAEngine


def main():
    reports = RCAEngine().diagnose_all()

    if not reports:
        print("No regressions to diagnose. Run Section 7's regression detection first.")
        return

    for r in reports:
        print(f"\n{'=' * 70}")
        print(f"Window: {r['window_start']}   category={r['root_cause_category']}   "
              f"confidence={r['confidence']}")
        print(f"{'=' * 70}")
        print(r["summary"])
        print(f"\n(rule-based finding, {len(r['regression_ids'])} regression(s) as evidence)")


if __name__ == "__main__":
    main()
