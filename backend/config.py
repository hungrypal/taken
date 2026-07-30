"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings for the API.

    Keep secrets out of source control. The development defaults make the
    project easy to start locally; production refuses the default JWT secret.
    """

    app_name: str = os.getenv("APP_NAME", "TerraScore Climate ML API")
    environment: str = os.getenv("ENVIRONMENT", "development").lower()
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./terrascore.db")
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY", "change-this-development-secret-before-deployment"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:4173"
        ).split(",")
    )
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    weather_api_base_url: str = os.getenv("WEATHER_API_BASE_URL", "https://api.open-meteo.com/v1/forecast")

    def validate_security_settings(self) -> None:
        """Prevent an accidental deployment with the public development key."""
        if self.environment in {"production", "prod"} and self.jwt_secret_key == (
            "change-this-development-secret-before-deployment"
        ):
            raise RuntimeError("JWT_SECRET_KEY must be configured in production.")


settings = Settings()
