"""
ORM model for detected regressions. Shares the same Base as
sentinel/trace/models.py.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Float, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..trace.models import Base


class Regression(Base):
    __tablename__ = "regressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    metric_name: Mapped[str] = mapped_column(String, index=True)
    method: Mapped[str] = mapped_column(String)  # "threshold" | "zscore" | "trend"
    severity: Mapped[str] = mapped_column(String)  # "warning" | "critical"

    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    window_minutes: Mapped[int] = mapped_column(Integer)

    baseline_value: Mapped[float] = mapped_column(Float, nullable=True)
    current_value: Mapped[float] = mapped_column(Float)
    delta_pct: Mapped[float] = mapped_column(Float, nullable=True)

    description: Mapped[str] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
