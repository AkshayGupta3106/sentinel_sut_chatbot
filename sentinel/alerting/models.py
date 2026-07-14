"""
ORM model for alert send attempts. Every attempt (successful, skipped,
or failed) gets a row, keyed by (alert_type, reference_id) -- that's
what powers deduplication: a regression already successfully alerted
on should never fire twice.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Boolean, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from ..trace.models import Base


class AlertLog(Base):
    __tablename__ = "alert_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    alert_type: Mapped[str] = mapped_column(String, index=True)  # "regression" | "rca" | "digest"
    reference_id: Mapped[str] = mapped_column(String, index=True)

    success: Mapped[bool] = mapped_column(Boolean)
    error: Mapped[str] = mapped_column(Text, nullable=True)

    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
