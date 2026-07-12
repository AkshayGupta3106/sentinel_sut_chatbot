"""
ORM models for assembled traces.

This is a working preview of Section 9's full schema -- just the two
tables Section 4 actually needs (`traces`, `trace_events`). The other
tables (evaluations, metrics_timeseries, regressions, rca_reports) get
added when those sections build them, on top of the same Base.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Trace(Base):
    __tablename__ = "traces"

    trace_id: Mapped[str] = mapped_column(String, primary_key=True)
    query_id: Mapped[str] = mapped_column(String, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_latency_ms: Mapped[float] = mapped_column(Float)

    num_stages: Mapped[int] = mapped_column(Integer)
    slowest_stage: Mapped[str] = mapped_column(String, nullable=True)
    slowest_stage_latency_ms: Mapped[float] = mapped_column(Float, nullable=True)

    has_error: Mapped[bool] = mapped_column(Boolean, default=False)
    error_stage: Mapped[str] = mapped_column(String, nullable=True)

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    events: Mapped[list["TraceEvent"]] = relationship(back_populates="trace", cascade="all, delete-orphan")


class TraceEvent(Base):
    __tablename__ = "trace_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    trace_id: Mapped[str] = mapped_column(ForeignKey("traces.trace_id"))

    stage_name: Mapped[str] = mapped_column(String, index=True)
    stage_order: Mapped[int] = mapped_column(Integer)

    timestamp_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    timestamp_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latency_ms: Mapped[float] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String)
    error: Mapped[str] = mapped_column(Text, nullable=True)

    input_summary: Mapped[dict] = mapped_column(JSON, nullable=True)
    output_summary: Mapped[dict] = mapped_column(JSON, nullable=True)
    event_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    trace: Mapped["Trace"] = relationship(back_populates="events")
