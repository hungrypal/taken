"""Adapter around the existing ML inference pipeline for batch workflows."""

from __future__ import annotations


class MLService:
    """Reuse the established pipeline without duplicating feature logic."""

    def predict(self, latitude: float, longitude: float, start_date: str, end_date: str) -> dict:
        # Local import avoids a router/application import cycle during startup.
        from backend.api import execute_prediction

        return execute_prediction(latitude, longitude, start_date, end_date)


ml_service = MLService()
