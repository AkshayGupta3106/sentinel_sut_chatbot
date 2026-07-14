"""
HTML Report Generator.

Pulls from Section 9's SentinelRepository and renders a single
self-contained HTML file -- summary stats, recent regressions, RCA
highlights, worst-performing traces. No external JS/CSS dependency, so
the report opens correctly even offline or attached to an email.
"""

from datetime import datetime, timezone

from jinja2 import Template

from ..repository import SentinelRepository

TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Sentinel AI Report — {{ generated_at }}</title>
<style>
  body { font-family: -apple-system, Segoe UI, Roboto, sans-serif; background: #0f1115; color: #e6e6e6; margin: 0; padding: 40px; }
  h1 { font-size: 22px; }
  h2 { font-size: 16px; color: #9aa5b1; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 40px; }
  .stats { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0 32px; }
  .stat-card { background: #1a1d24; border: 1px solid #2a2e37; border-radius: 8px; padding: 16px 20px; min-width: 140px; }
  .stat-card .value { font-size: 26px; font-weight: 600; }
  .stat-card .label { font-size: 12px; color: #9aa5b1; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #2a2e37; font-size: 13px; }
  th { color: #9aa5b1; font-weight: 500; }
  .severity-critical { color: #e74c3c; font-weight: 600; }
  .severity-warning { color: #f1c40f; font-weight: 600; }
  .confidence-high { color: #2ecc71; }
  .confidence-medium { color: #f1c40f; }
  .confidence-low { color: #e74c3c; }
  .empty { color: #6b7280; font-style: italic; }
</style>
</head>
<body>
  <h1>🛡️ Sentinel AI — Observability Report</h1>
  <p style="color:#9aa5b1;">Generated {{ generated_at }}</p>

  <div class="stats">
    {% for label, value in stats.items() %}
    <div class="stat-card">
      <div class="value">{{ value }}</div>
      <div class="label">{{ label.replace('_', ' ') }}</div>
    </div>
    {% endfor %}
  </div>

  <h2>Recent Regressions</h2>
  {% if regressions %}
  <table>
    <tr><th>Metric</th><th>Method</th><th>Severity</th><th>Window</th><th>Description</th></tr>
    {% for r in regressions %}
    <tr>
      <td>{{ r.metric_name }}</td>
      <td>{{ r.method }}</td>
      <td class="severity-{{ r.severity }}">{{ r.severity }}</td>
      <td>{{ r.window_start }}</td>
      <td>{{ r.description }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="empty">No regressions on record.</p>
  {% endif %}

  <h2>Root Cause Analysis Highlights</h2>
  {% if rca_reports %}
  <table>
    <tr><th>Window</th><th>Category</th><th>Confidence</th><th>Summary</th></tr>
    {% for r in rca_reports %}
    <tr>
      <td>{{ r.window_start }}</td>
      <td>{{ r.root_cause_category }}</td>
      <td class="confidence-{{ r.confidence }}">{{ r.confidence }}</td>
      <td>{{ r.summary }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="empty">No RCA reports on record.</p>
  {% endif %}

  <h2>Worst-Performing Recent Traces</h2>
  {% if worst_traces %}
  <table>
    <tr><th>Trace ID</th><th>Started</th><th>Stages</th><th>Total Latency (ms)</th><th>Slowest Stage</th><th>Status</th></tr>
    {% for t in worst_traces %}
    <tr>
      <td>{{ t.trace_id[:8] }}...</td>
      <td>{{ t.started_at }}</td>
      <td>{{ t.num_stages }}</td>
      <td>{{ "%.2f"|format(t.total_latency_ms) }}</td>
      <td>{{ t.slowest_stage }}</td>
      <td>{{ "❌ error" if t.has_error else "✅ success" }}</td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <p class="empty">No traces on record.</p>
  {% endif %}

</body>
</html>
"""


def generate_html_report(output_path: str = "sentinel_report.html", top_n: int = 10) -> str:
    repo = SentinelRepository()
    stats = repo.get_summary_stats()
    regressions = repo.get_open_regressions(limit=top_n)
    rca_reports = repo.get_rca_reports(limit=top_n)

    recent_traces = repo.get_recent_traces(limit=200)
    worst_traces = sorted(recent_traces, key=lambda t: t.total_latency_ms, reverse=True)[:top_n]

    html = Template(TEMPLATE).render(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        stats=stats,
        regressions=regressions,
        rca_reports=rca_reports,
        worst_traces=worst_traces,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
