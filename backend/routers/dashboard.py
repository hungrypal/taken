"""Authenticated dashboard aggregates generated directly from SQLAlchemy."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.farm import Farm
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.routers.auth import get_current_user


router = APIRouter(tags=["dashboard"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


def base_prediction_filter(user_id: int):
    return Prediction.user_id == user_id


@router.get("/dashboard", summary="Get dashboard summary")
def dashboard(user: CurrentUser, db: DatabaseSession) -> dict:
    """Return KPI cards for the authenticated user's farms and predictions."""
    predicate = base_prediction_filter(user.id)
    total = db.scalar(select(func.count(Prediction.id)).where(predicate)) or 0
    average_credit = db.scalar(select(func.avg(Prediction.credit_score)).where(predicate))
    average_ndvi = db.scalar(select(func.avg(Prediction.ndvi)).where(predicate))
    average_temperature = db.scalar(select(func.avg(Prediction.lst)).where(predicate))
    high_risk = db.scalar(select(func.count(Prediction.id)).where(predicate, Prediction.risk_classification == "High Risk")) or 0
    healthy_farms = db.scalar(select(func.count(Farm.id)).where(Farm.user_id == user.id, Farm.is_active.is_(True))) or 0
    return {"total_predictions": total, "average_credit_score": round(float(average_credit or 0), 2), "high_risk_farms": high_risk, "healthy_farms": healthy_farms, "average_ndvi": round(float(average_ndvi or 0), 3), "average_temperature": round(float(average_temperature or 0), 2)}


@router.get("/analytics", summary="Get daily prediction trends")
def analytics(user: CurrentUser, db: DatabaseSession) -> dict:
    """Return the last 30 days of daily prediction and credit-score trends."""
    since = datetime.now(timezone.utc) - timedelta(days=30)
    rows = db.execute(
        select(func.date(Prediction.created_at).label("date"), func.count(Prediction.id).label("predictions"), func.avg(Prediction.credit_score).label("average_credit_score"), func.avg(Prediction.ndvi).label("average_ndvi"))
        .where(Prediction.user_id == user.id, Prediction.created_at >= since)
        .group_by(func.date(Prediction.created_at)).order_by(func.date(Prediction.created_at))
    ).all()
    return {"prediction_trends": [{"date": str(row.date), "predictions": row.predictions, "average_credit_score": round(float(row.average_credit_score), 2), "average_ndvi": round(float(row.average_ndvi), 3)} for row in rows]}
