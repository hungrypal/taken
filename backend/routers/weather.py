"""Weather forecast API backed by the weather service."""

from fastapi import APIRouter, HTTPException, Query

from backend.services.weather_service import WeatherServiceError, weather_service


router = APIRouter(tags=["weather"])


@router.get("/forecast", summary="Get seven-day farm weather forecast")
def forecast(
    latitude: float = Query(..., ge=-90, le=90, examples=[28.4]),
    longitude: float = Query(..., ge=-180, le=180, examples=[77.0]),
) -> dict:
    """Return normalized daily temperature, rainfall, humidity, and wind data."""
    try:
        return {"latitude": latitude, "longitude": longitude, "days": weather_service.seven_day_forecast(latitude, longitude)}
    except WeatherServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
