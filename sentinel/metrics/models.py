"""
ORM model for time-windowed metric rollups.

Shares the same Base as sentinel/trace/models.py -- one database, and
Base.metadata.create_all() in trace/db.py picks up this table too as
long as this module gets imported before init_db() runs.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..trace.models import Base


class MetricPoint(Base):
    __tablename__ = "metrics_timeseries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    window_minutes: Mapped[int] = mapped_column(Integer, index=True)

    metric_name: Mapped[str] = mapped_column(String, index=True)
    value: Mapped[float] = mapped_column(Float)

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
