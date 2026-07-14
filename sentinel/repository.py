"""
Data Access Layer.

Centralizes read queries across all 6 tables (traces, trace_events,
metrics_timeseries, evaluations, regressions, rca_reports) so
dashboard and report code doesn't scatter raw
`session.execute(select(...))` calls everywhere.

Deliberately read-only: writes still live inside each section's own
engine (TraceAssembler, MetricsCollector, EvaluationEngine,
RegressionEngine, RCAEngine) since those are the components that
actually know how to construct valid rows for their own tables. This
repository is for Section 10's reporting layer and beyond to read
from, not to write through.
"""

from sqlalchemy import select, func

from .trace.db import get_session, init_db
from .trace.models import Trace, TraceEvent
from .metrics.models import MetricPoint
from .evaluation.models import Evaluation
from .regression.models import Regression
from .rca.models import RCAReport


class SentinelRepository:
    def __init__(self):
        init_db()

    def get_recent_traces(self, limit: int = 20) -> list[Trace]:
        session = get_session()
        try:
            return session.execute(
                select(Trace).order_by(Trace.started_at.desc()).limit(limit)
            ).scalars().all()
        finally:
            session.close()

    def get_trace_detail(self, trace_id: str) -> dict:
        session = get_session()
        try:
            trace = session.execute(select(Trace).where(Trace.trace_id == trace_id)).scalar_one_or_none()
            if not trace:
                return {}
            events = session.execute(
                select(TraceEvent).where(TraceEvent.trace_id == trace_id).order_by(TraceEvent.stage_order)
            ).scalars().all()
            evaluations = session.execute(
                select(Evaluation).where(Evaluation.trace_id == trace_id)
            ).scalars().all()
            return {"trace": trace, "events": events, "evaluations": evaluations}
        finally:
            session.close()

    def get_open_regressions(self, limit: int = 50) -> list[Regression]:
        session = get_session()
        try:
            return session.execute(
                select(Regression).order_by(Regression.window_start.desc()).limit(limit)
            ).scalars().all()
        finally:
            session.close()

    def get_rca_reports(self, limit: int = 50) -> list[RCAReport]:
        session = get_session()
        try:
            return session.execute(
                select(RCAReport).order_by(RCAReport.window_start.desc()).limit(limit)
            ).scalars().all()
        finally:
            session.close()

    def get_summary_stats(self) -> dict:
        session = get_session()
        try:
            return {
                "total_traces": session.execute(select(func.count()).select_from(Trace)).scalar() or 0,
                "total_evaluations": session.execute(select(func.count()).select_from(Evaluation)).scalar() or 0,
                "total_regressions": session.execute(select(func.count()).select_from(Regression)).scalar() or 0,
                "total_rca_reports": session.execute(select(func.count()).select_from(RCAReport)).scalar() or 0,
                "error_traces": session.execute(
                    select(func.count()).select_from(Trace).where(Trace.has_error == True)
                ).scalar() or 0,
            }
        finally:
            session.close()

    # --- Bulk reads, for export/reporting rather than dashboard display ---

    def get_all_traces(self) -> list[Trace]:
        session = get_session()
        try:
            return session.execute(select(Trace)).scalars().all()
        finally:
            session.close()

    def get_all_trace_events(self) -> list[TraceEvent]:
        session = get_session()
        try:
            return session.execute(select(TraceEvent)).scalars().all()
        finally:
            session.close()

    def get_all_metric_points(self) -> list[MetricPoint]:
        session = get_session()
        try:
            return session.execute(select(MetricPoint)).scalars().all()
        finally:
            session.close()

    def get_all_evaluations(self) -> list[Evaluation]:
        session = get_session()
        try:
            return session.execute(select(Evaluation)).scalars().all()
        finally:
            session.close()

    def get_all_regressions(self) -> list[Regression]:
        session = get_session()
        try:
            return session.execute(select(Regression)).scalars().all()
        finally:
            session.close()

    def get_all_rca_reports(self) -> list[RCAReport]:
        session = get_session()
        try:
            return session.execute(select(RCAReport)).scalars().all()
        finally:
            session.close()
