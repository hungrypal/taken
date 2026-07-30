"""Validated contracts for farms, histories, analytics, and file ingestion."""

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Coordinates(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class FarmCreate(Coordinates):
    model_config = ConfigDict(json_schema_extra={"example": {"farm_name": "North Field", "latitude": 28.4, "longitude": 77.0, "crop": "Wheat", "area": 2.5}})
    farm_name: str = Field(min_length=1, max_length=120)
    crop: Optional[str] = Field(default=None, max_length=80)
    area: Optional[float] = Field(default=None, gt=0, le=100_000)


class FarmUpdate(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"crop": "Millet", "area": 3.0}})
    farm_name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    crop: Optional[str] = Field(default=None, max_length=80)
    area: Optional[float] = Field(default=None, gt=0, le=100_000)


class FarmResponse(FarmCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Recommendation(BaseModel):
    category: str
    message: str
    priority: str


class StoredPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    farm_id: Optional[int]
    latitude: float
    longitude: float
    prediction_date: date
    drought_index: float
    ndvi: float
    lst: float
    climate: Optional[dict[str, Any]]
    credit_score: float
    risk_classification: str
    recommendations: Optional[list[Recommendation]]
    created_at: datetime


class ForecastQuery(Coordinates):
    pass


class UploadPredictionRow(Coordinates):
    farm_name: Optional[str] = None
    crop: Optional[str] = None
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, end_date: date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date must be on or after start_date")
        return end_date
