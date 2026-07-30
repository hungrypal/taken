"""Metadata for every model training attempt."""

from __future__ import annotations

from datetime import date, datetime, timezone

from typing import Any, Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base


class TrainingHistory(Base):
    """Auditable record of an ML training run and its resulting metrics."""

    __tablename__ = "training_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="completed", nullable=False)
    model_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional["User"]] = relationship(back_populates="training_runs")
