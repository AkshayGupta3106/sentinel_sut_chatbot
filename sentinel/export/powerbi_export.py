"""
Power BI Export Layer.

Power BI Desktop isn't available in this sandbox -- there is no real
.pbix file to hand over here, and producing a fake one would just be
lying about it. What's real and testable is this: exporting every
table to CSV + Parquet in a form Power BI can actually import and
build relationships against. docs/POWERBI_GUIDE.md walks through
exactly how, step by step.

One non-trivial modeling detail this handles: rca_reports.regression_ids
is a JSON array (one report can cite several regressions), which Power
BI can't turn into a relationship by itself. This exports a proper
bridge/junction table instead -- one row per (rca_report_id,
regression_id) pair -- which is the standard star-schema way to model
a many-to-many relationship in any BI tool, Power BI included.
"""

import os

import pandas as pd

from ..repository import SentinelRepository

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "powerbi_exports")


def _to_df(rows, columns_fn) -> pd.DataFrame:
    return pd.DataFrame([columns_fn(r) for r in rows])


def _write(df: pd.DataFrame, name: str) -> tuple[str, str]:
    os.makedirs(EXPORT_DIR, exist_ok=True)
    csv_path = os.path.join(EXPORT_DIR, f"{name}.csv")
    parquet_path = os.path.join(EXPORT_DIR, f"{name}.parquet")
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)
    print(f"  {name:<24} {len(df):>5} rows  -> {csv_path}")
    return csv_path, parquet_path


def export_all() -> str:
    repo = SentinelRepository()

    traces_df = _to_df(repo.get_all_traces(), lambda t: {
        "trace_id": t.trace_id, "query_id": t.query_id,
        "started_at": t.started_at, "ended_at": t.ended_at,
        "total_latency_ms": t.total_latency_ms, "num_stages": t.num_stages,
        "slowest_stage": t.slowest_stage, "slowest_stage_latency_ms": t.slowest_stage_latency_ms,
        "has_error": t.has_error, "error_stage": t.error_stage,
    })

    trace_events_df = _to_df(repo.get_all_trace_events(), lambda e: {
        "event_id": e.event_id, "trace_id": e.trace_id,
        "stage_name": e.stage_name, "stage_order": e.stage_order,
        "timestamp_start": e.timestamp_start, "timestamp_end": e.timestamp_end,
        "latency_ms": e.latency_ms, "status": e.status, "error": e.error,
    })

    metrics_df = _to_df(repo.get_all_metric_points(), lambda m: {
        "id": m.id, "window_start": m.window_start, "window_end": m.window_end,
        "window_minutes": m.window_minutes, "metric_name": m.metric_name, "value": m.value,
    })

    evaluations_df = _to_df(repo.get_all_evaluations(), lambda ev: {
        "id": ev.id, "trace_id": ev.trace_id, "evaluator_name": ev.evaluator_name,
        "score": ev.score, "reasoning": ev.reasoning, "skipped": ev.skipped,
        "created_at": ev.created_at,
    })

    regressions_df = _to_df(repo.get_all_regressions(), lambda r: {
        "id": r.id, "metric_name": r.metric_name, "method": r.method, "severity": r.severity,
        "window_start": r.window_start, "window_minutes": r.window_minutes,
        "baseline_value": r.baseline_value, "current_value": r.current_value,
        "delta_pct": r.delta_pct, "description": r.description, "detected_at": r.detected_at,
    })

    rca_reports = repo.get_all_rca_reports()
    rca_reports_df = _to_df(rca_reports, lambda r: {
        "id": r.id, "window_start": r.window_start, "root_cause_category": r.root_cause_category,
        "confidence": r.confidence, "summary": r.summary, "created_at": r.created_at,
    })

    bridge_rows = [
        {"rca_report_id": r.id, "regression_id": reg_id}
        for r in rca_reports for reg_id in (r.regression_ids or [])
    ]
    bridge_df = pd.DataFrame(bridge_rows, columns=["rca_report_id", "regression_id"])

    print(f"Exporting to {os.path.abspath(EXPORT_DIR)}\n")
    _write(traces_df, "traces")
    _write(trace_events_df, "trace_events")
    _write(metrics_df, "metrics_timeseries")
    _write(evaluations_df, "evaluations")
    _write(regressions_df, "regressions")
    _write(rca_reports_df, "rca_reports")
    _write(bridge_df, "rca_regression_bridge")

    return EXPORT_DIR


def export_combined_evaluation_report() -> str:
    """
    A single flat table: one row per trace, with every evaluator's
    score as its own column (heuristic_faithfulness_overlap,
    heuristic_relevance_keyword, llm_judge_faithfulness,
    llm_judge_relevance), joined against that trace's own latency/
    error/source info.

    This trades relational correctness for convenience -- no
    relationships to set up in Power BI, just one table you can build
    every Evaluation-tab visual directly against. The 7-table export
    (export_all) is still the more "correct" model for anything beyond
    the Evaluation view; use this one when you just want to move fast.
    """
    repo = SentinelRepository()
    traces = repo.get_all_traces()
    evaluations = repo.get_all_evaluations()

    traces_df = _to_df(traces, lambda t: {
        "trace_id": t.trace_id,
        "started_at": t.started_at,
        "total_latency_ms": t.total_latency_ms,
        "num_stages": t.num_stages,
        "slowest_stage": t.slowest_stage,
        "slowest_stage_latency_ms": t.slowest_stage_latency_ms,
        "has_error": t.has_error,
        "error_stage": t.error_stage,
    })

    if not evaluations:
        combined = traces_df.copy()
        for col in ["heuristic_faithfulness_overlap", "heuristic_relevance_keyword",
                    "llm_judge_faithfulness", "llm_judge_relevance"]:
            combined[col] = None
    else:
        eval_df = _to_df(evaluations, lambda e: {
            "trace_id": e.trace_id, "evaluator_name": e.evaluator_name, "score": e.score,
        })
        # Pivot: one row per trace_id, one column per evaluator_name
        # dropna=False matters here: pivot_table's default (dropna=True)
        # silently deletes any evaluator column that's entirely NaN --
        # which is exactly what happens to llm_judge_* columns whenever
        # no GEMINI_API_KEY is set (score=None for every row). Without
        # this, those columns would vanish from the export instead of
        # showing up as an honest all-null column.
        pivot = eval_df.pivot_table(
            index="trace_id", columns="evaluator_name", values="score",
            aggfunc="first", dropna=False,
        ).reset_index()

        combined = traces_df.merge(pivot, on="trace_id", how="left")

    # A convenience "overall_quality" average across whichever evaluator
    # columns are actually present and non-null for that row -- makes a
    # single-number KPI card trivial to build in Power BI.
    score_cols = [c for c in combined.columns if "faithfulness" in c or "relevance" in c]
    if score_cols:
        combined["avg_quality_score"] = combined[score_cols].mean(axis=1, skipna=True)

    os.makedirs(EXPORT_DIR, exist_ok=True)
    csv_path = os.path.join(EXPORT_DIR, "combined_evaluation_report.csv")
    parquet_path = os.path.join(EXPORT_DIR, "combined_evaluation_report.parquet")
    combined.to_csv(csv_path, index=False)
    combined.to_parquet(parquet_path, index=False)

    print(f"Combined evaluation report: {len(combined)} rows -> {csv_path}")
    return csv_path


if __name__ == "__main__":
    export_all()
    export_combined_evaluation_report()
