"""
ORM model for root cause analysis reports. Shares the same Base as
sentinel/trace/models.py.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..trace.models import Base


class RCAReport(Base):
    __tablename__ = "rca_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, unique=True)

    regression_ids: Mapped[list] = mapped_column(JSON)
    root_cause_category: Mapped[str] = mapped_column(String)
    confidence: Mapped[str] = mapped_column(String)  # "high" | "medium" | "low"
    summary: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
