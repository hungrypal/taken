"""Authenticated prediction history queries and deletion."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas.domain import StoredPredictionResponse


router = APIRouter(tags=["prediction history"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


def owned_prediction(prediction_id: int, user: User, db: Session) -> Prediction:
    prediction = db.get(Prediction, prediction_id)
    if prediction is None or prediction.user_id != user.id:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@router.get("/predictions", response_model=list[StoredPredictionResponse], summary="List my prediction history")
def list_predictions(user: CurrentUser, db: DatabaseSession) -> list[Prediction]:
    return list(db.scalars(select(Prediction).where(Prediction.user_id == user.id).order_by(Prediction.created_at.desc())))


@router.get("/prediction/{prediction_id}", response_model=StoredPredictionResponse, summary="Get one prediction")
def get_prediction(prediction_id: int, user: CurrentUser, db: DatabaseSession) -> Prediction:
    return owned_prediction(prediction_id, user, db)


@router.delete("/prediction/{prediction_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete one prediction")
def delete_prediction(prediction_id: int, user: CurrentUser, db: DatabaseSession) -> None:
    db.delete(owned_prediction(prediction_id, user, db))
    db.commit()
