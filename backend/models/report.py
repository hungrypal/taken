"""Generated report metadata and durable report payloads."""

from __future__ import annotations

from datetime import datetime, timezone

from typing import Any, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.session import Base


class Report(Base):
    """A generated business report linked to its farm and/or prediction."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    farm_id: Mapped[Optional[int]] = mapped_column(ForeignKey("farms.id", ondelete="SET NULL"), index=True)
    prediction_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("predictions.id", ondelete="SET NULL"), index=True
    )
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="generated", nullable=False)
    storage_uri: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    report_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship(back_populates="reports")
    farm: Mapped[Optional["Farm"]] = relationship(back_populates="reports")
    prediction: Mapped[Optional["Prediction"]] = relationship(back_populates="reports")
