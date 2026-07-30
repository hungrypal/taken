"""Resilient Open-Meteo weather forecast client."""

from datetime import date

import requests

from backend.config import settings


class WeatherServiceError(Exception):
    """Raised when the upstream weather provider cannot supply a forecast."""


class WeatherService:
    """Fetch and normalize a seven-day forecast from Open-Meteo."""

    def seven_day_forecast(self, latitude: float, longitude: float) -> list[dict[str, float | str]]:
        try:
            response = requests.get(
                settings.weather_api_base_url,
                params={"latitude": latitude, "longitude": longitude, "daily": "temperature_2m_max,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max", "timezone": "auto", "forecast_days": 7},
                timeout=10,
            )
            response.raise_for_status()
            daily = response.json()["daily"]
            return [
                {"date": daily["time"][index], "temperature": daily["temperature_2m_max"][index], "rainfall": daily["precipitation_sum"][index], "humidity": daily["relative_humidity_2m_mean"][index], "wind_speed": daily["wind_speed_10m_max"][index]}
                for index in range(min(7, len(daily["time"])))
            ]
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            raise WeatherServiceError("Weather forecast is temporarily unavailable.") from exc


weather_service = WeatherService()
