# Sentinel AI — Schema Overview (auto-generated)

Regenerate with `python -m sentinel.export_schema`. Do not hand-edit.

## `alert_log`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | INTEGER | ✓ |  | NOT NULL |
| alert_type | VARCHAR |  |  | NOT NULL |
| reference_id | VARCHAR |  |  | NOT NULL |
| success | BOOLEAN |  |  | NOT NULL |
| error | TEXT |  |  |  |
| sent_at | DATETIME |  |  | NOT NULL |

## `metrics_timeseries`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | INTEGER | ✓ |  | NOT NULL |
| window_start | DATETIME |  |  | NOT NULL |
| window_end | DATETIME |  |  | NOT NULL |
| window_minutes | INTEGER |  |  | NOT NULL |
| metric_name | VARCHAR |  |  | NOT NULL |
| value | FLOAT |  |  | NOT NULL |
| computed_at | DATETIME |  |  | NOT NULL |

## `rca_reports`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | INTEGER | ✓ |  | NOT NULL |
| window_start | DATETIME |  |  | NOT NULL |
| regression_ids | JSON |  |  | NOT NULL |
| root_cause_category | VARCHAR |  |  | NOT NULL |
| confidence | VARCHAR |  |  | NOT NULL |
| summary | TEXT |  |  | NOT NULL |
| created_at | DATETIME |  |  | NOT NULL |

## `regressions`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | INTEGER | ✓ |  | NOT NULL |
| metric_name | VARCHAR |  |  | NOT NULL |
| method | VARCHAR |  |  | NOT NULL |
| severity | VARCHAR |  |  | NOT NULL |
| window_start | DATETIME |  |  | NOT NULL |
| window_minutes | INTEGER |  |  | NOT NULL |
| baseline_value | FLOAT |  |  |  |
| current_value | FLOAT |  |  | NOT NULL |
| delta_pct | FLOAT |  |  |  |
| description | TEXT |  |  | NOT NULL |
| detected_at | DATETIME |  |  | NOT NULL |

## `traces`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| trace_id | VARCHAR | ✓ |  | NOT NULL |
| query_id | VARCHAR |  |  |  |
| started_at | DATETIME |  |  | NOT NULL |
| ended_at | DATETIME |  |  | NOT NULL |
| total_latency_ms | FLOAT |  |  | NOT NULL |
| num_stages | INTEGER |  |  | NOT NULL |
| slowest_stage | VARCHAR |  |  |  |
| slowest_stage_latency_ms | FLOAT |  |  |  |
| has_error | BOOLEAN |  |  | NOT NULL |
| error_stage | VARCHAR |  |  |  |
| ingested_at | DATETIME |  |  | NOT NULL |

## `evaluations`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| id | INTEGER | ✓ |  | NOT NULL |
| trace_id | VARCHAR |  | traces.trace_id | NOT NULL |
| evaluator_name | VARCHAR |  |  | NOT NULL |
| score | FLOAT |  |  |  |
| reasoning | TEXT |  |  |  |
| skipped | BOOLEAN |  |  | NOT NULL |
| created_at | DATETIME |  |  | NOT NULL |

## `trace_events`

| Column | Type | PK | FK | Nullable |
|---|---|---|---|---|
| event_id | VARCHAR | ✓ |  | NOT NULL |
| trace_id | VARCHAR |  | traces.trace_id | NOT NULL |
| stage_name | VARCHAR |  |  | NOT NULL |
| stage_order | INTEGER |  |  | NOT NULL |
| timestamp_start | DATETIME |  |  | NOT NULL |
| timestamp_end | DATETIME |  |  | NOT NULL |
| latency_ms | FLOAT |  |  | NOT NULL |
| status | VARCHAR |  |  | NOT NULL |
| error | TEXT |  |  |  |
| input_summary | JSON |  |  |  |
| output_summary | JSON |  |  |  |
| event_metadata | JSON |  |  |  |
