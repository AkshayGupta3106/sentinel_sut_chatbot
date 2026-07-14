# Section 11 — Power BI Dashboard Build Guide

This is the honest version of Section 11: Power BI Desktop is a real,
separate application that isn't available in the sandbox this project
was built in, so there is no fake `.pbix` file here. What's real is
the data export (`sentinel/export/powerbi_export.py`) and this guide —
follow it in your own Power BI Desktop and it should take about 20-30
minutes to build the real thing.

## 1. Generate the export

```bash
python -m sentinel.export.powerbi_export
```

This writes 7 tables to `powerbi_exports/`, as both `.csv` and
`.parquet` (use whichever Power BI's version on your machine prefers —
recent Power BI Desktop reads Parquet natively):

| File | What it is |
|---|---|
| `traces.csv` | One row per query, with total latency, slowest stage, error flag |
| `trace_events.csv` | One row per pipeline stage per query (8 rows per trace) |
| `metrics_timeseries.csv` | Time-windowed rollups (p50/p95/p99 latency, error rate, per-stage avg) |
| `evaluations.csv` | Faithfulness/relevance scores per trace |
| `regressions.csv` | Every regression flagged by Section 7 |
| `rca_reports.csv` | Every root-cause diagnosis from Section 8 |
| `rca_regression_bridge.csv` | Junction table: which regressions each RCA report cites (many-to-many) |

Re-run this script any time you want the Power BI report to reflect
new data — it's a full re-export, not an incremental one.

## 2. Import into Power BI Desktop

`Get Data` → `Text/CSV` (or `Parquet` if available) → select all 7
files from `powerbi_exports/` → `Load` (not "Transform Data", unless
you want to fix column types manually first — see step 3).

## 3. Fix column types (Power Query)

Power BI usually infers types correctly, but check these explicitly in
`Transform Data`:

- `traces.started_at`, `traces.ended_at` → **Date/Time**
- `trace_events.timestamp_start`, `timestamp_end` → **Date/Time**
- `metrics_timeseries.window_start`, `window_end` → **Date/Time**
- `regressions.window_start`, `evaluations.created_at`, `rca_reports.window_start` → **Date/Time**
- `traces.has_error`, `evaluations.skipped` → **True/False**

## 4. Set up relationships (Model view)

| From | To | Cardinality |
|---|---|---|
| `traces[trace_id]` | `trace_events[trace_id]` | 1 → many |
| `traces[trace_id]` | `evaluations[trace_id]` | 1 → many |
| `rca_reports[id]` | `rca_regression_bridge[rca_report_id]` | 1 → many |
| `regressions[id]` | `rca_regression_bridge[regression_id]` | 1 → many |

`metrics_timeseries` and `regressions` don't need a direct relationship
to `traces` — they're aggregates over time windows, not per-trace rows.
Filter/slice them independently by `window_start`.

The bridge table is why `rca_regression_bridge.csv` exists at all:
`rca_reports.regression_ids` was a JSON array in the source DB (one
report can cite several regressions), and Power BI can't build a
relationship directly on a JSON column — the bridge table is the
standard star-schema fix, one row per (report, regression) pair.

## 5. DAX measures to create

In `traces`, add these as new measures:

```dax
Avg Trace Latency (ms) = AVERAGE(traces[total_latency_ms])

Error Rate % =
DIVIDE(
    CALCULATE(COUNTROWS(traces), traces[has_error] = TRUE),
    COUNTROWS(traces)
)

P95 Trace Latency (ms) = PERCENTILE.INC(traces[total_latency_ms], 0.95)
```

In `evaluations`:

```dax
Avg Faithfulness Score =
CALCULATE(
    AVERAGE(evaluations[score]),
    evaluations[evaluator_name] IN {"heuristic_faithfulness_overlap", "llm_judge_faithfulness"}
)

Avg Relevance Score =
CALCULATE(
    AVERAGE(evaluations[score]),
    evaluations[evaluator_name] IN {"heuristic_relevance_keyword", "llm_judge_relevance"}
)
```

In `regressions`:

```dax
Critical Regression Count =
CALCULATE(COUNTROWS(regressions), regressions[severity] = "critical")
```

## 6. Build the 5 core views

**View 1 — System Health Overview**
- Line chart: `metrics_timeseries[window_start]` (axis) × `value` (y),
  filtered to `metric_name = "latency_p95_ms"` and `"error_rate_pct"`,
  split by `metric_name` (legend)
- Card visuals: `Avg Trace Latency (ms)`, `Error Rate %`

**View 2 — Quality Trends**
- Line chart: `evaluations[created_at]` (axis) × `Avg Faithfulness
  Score` and `Avg Relevance Score` (y, two lines)
- Table: `evaluations` filtered to `skipped = FALSE`, columns
  `trace_id`, `evaluator_name`, `score`, `reasoning`

**View 3 — Regression Timeline**
- Line chart of the relevant metric from `metrics_timeseries` (e.g.
  `stage_latency_avg_ms:chromadb_retrieval`) over `window_start`
- Overlay: scatter/marker layer from `regressions`, filtered to the
  same `metric_name`, plotted at `window_start` × `current_value` —
  this annotates exactly where each regression fired directly on the
  trend line
- Table below: `regressions` columns `metric_name`, `method`,
  `severity`, `delta_pct`, `description`

**View 4 — Stage Breakdown**
- Bar chart: `trace_events[stage_name]` (axis) × average
  `latency_ms` (y) — instantly shows which of the 8 stages is the
  bottleneck, same insight as the Streamlit dashboard's stage chart
  but filterable/drillable in Power BI
- Stacked bar: same axis, split by `status` (success/error) to show
  error concentration per stage

**View 5 — RCA Drill-Down**
- Table: `rca_reports` columns `window_start`, `root_cause_category`,
  `confidence`, `summary`
- On row click (use a Power BI drillthrough page or a slicer synced to
  `rca_reports[id]`), filter `rca_regression_bridge` → `regressions` to
  show exactly which regression(s) that report cites as evidence

## 7. Filters/slicers

Add slicers for:
- Date range on `traces[started_at]` / `metrics_timeseries[window_start]`
- `trace_events[stage_name]` (multi-select)
- `regressions[severity]` (Critical/Warning)

## 8. Refreshing the report

This project doesn't have a live Postgres connection wired up (see
`sentinel/trace/db.py` — it runs on SQLite locally, by design, see
Section 4's notes on why). So refreshing means:

```bash
python -m sentinel.export.powerbi_export   # re-export from sentinel.db
```

then `Refresh` in Power BI (`Home` → `Refresh`), since the files at
the same paths just got overwritten. A real production version would
point Power BI at Postgres directly (`Get Data` → `PostgreSQL
database`) and use scheduled refresh via a gateway — noted as a
natural next step, not implemented here.
