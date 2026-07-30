"""Administrative API for managing users and inspecting all domain records."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.farm import Farm
from backend.models.prediction import Prediction
from backend.models.user import User
from backend.routers.auth import require_admin
from backend.schemas.auth import LoginRequest, TokenResponse, UserResponse
from backend.schemas.domain import FarmResponse, StoredPredictionResponse
from backend.services.auth import create_access_token, create_refresh_token, verify_password


router = APIRouter(prefix="/admin", tags=["admin"])
AdminUser = Annotated[User, Depends(require_admin)]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=TokenResponse, summary="Authenticate an administrator")
def admin_login(payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    """Issue tokens only when supplied credentials belong to an administrator."""
    user = db.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None or not user.is_active or not user.is_admin or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid administrator credentials", headers={"WWW-Authenticate": "Bearer"})
    from backend.config import settings
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=create_refresh_token(user.id), expires_in=settings.access_token_expire_minutes * 60)


@router.get("/users", response_model=list[UserResponse], summary="List all users")
def users(_: AdminUser, db: DatabaseSession) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user")
def delete_user(user_id: int, admin: AdminUser, db: DatabaseSession) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Administrators cannot delete themselves")
    db.delete(user)
    db.commit()


@router.get("/farms", response_model=list[FarmResponse], summary="List all farms")
def farms(_: AdminUser, db: DatabaseSession) -> list[Farm]:
    return list(db.scalars(select(Farm).order_by(Farm.created_at.desc())))


@router.get("/predictions", response_model=list[StoredPredictionResponse], summary="List all predictions")
def predictions(_: AdminUser, db: DatabaseSession) -> list[Prediction]:
    return list(db.scalars(select(Prediction).order_by(Prediction.created_at.desc())))


@router.get("/statistics", summary="Get platform statistics")
def statistics(_: AdminUser, db: DatabaseSession) -> dict:
    return {"users": db.scalar(select(func.count(User.id))) or 0, "farms": db.scalar(select(func.count(Farm.id))) or 0, "predictions": db.scalar(select(func.count(Prediction.id))) or 0, "average_credit_score": round(float(db.scalar(select(func.avg(Prediction.credit_score))) or 0), 2)}
