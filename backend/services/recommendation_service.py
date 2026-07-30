"""Deterministic agronomic recommendations derived from prediction inputs."""

from __future__ import annotations

from typing import Any


class RecommendationService:
    """Generate explainable, rule-based advice without changing ML outputs."""

    def generate(
        self, *, ndvi: float, lst: float, rainfall: float | None, temperature: float | None,
        humidity: float | None, credit_score: float
    ) -> list[dict[str, str]]:
        recommendations: list[dict[str, str]] = []
        if ndvi < 0.35:
            recommendations.append({"category": "fertilizer", "message": "Low vegetation health detected; assess soil nutrients and apply fertilizer after a soil test.", "priority": "high"})
        if rainfall is not None and rainfall < 3 and (lst > 30 or temperature and temperature > 30):
            recommendations.append({"category": "irrigation", "message": "Increase irrigation and monitor soil moisture because hot, dry conditions are likely.", "priority": "high"})
        if rainfall is not None and rainfall > 50:
            recommendations.append({"category": "flood", "message": "Flood warning: improve drainage and avoid field operations in saturated areas.", "priority": "high"})
        if ndvi < 0.45 and rainfall is not None and rainfall < 10:
            recommendations.append({"category": "drought", "message": "Drought warning: prioritize water-efficient practices and drought-tolerant crop varieties.", "priority": "high"})
        if humidity is not None and humidity > 85:
            recommendations.append({"category": "crop_health", "message": "High humidity may increase fungal disease pressure; inspect crops and improve airflow.", "priority": "medium"})
        crop_message = "Suitable crops: millet, sorghum, and pulses are resilient choices for current dry conditions." if ndvi < 0.45 else "Suitable crops: current vegetation conditions support cereals, pulses, and seasonal vegetables with local agronomy guidance."
        recommendations.append({"category": "crop_selection", "message": crop_message, "priority": "medium"})
        if credit_score < 50:
            recommendations.append({"category": "credit", "message": "Improve irrigation and crop-health records before the next credit assessment.", "priority": "medium"})
        return recommendations


recommendation_service = RecommendationService()
