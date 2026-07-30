"""Authenticated farm ownership and lifecycle endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.farm import Farm
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas.domain import FarmCreate, FarmResponse, FarmUpdate


router = APIRouter(prefix="/farm", tags=["farms"])
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


def owned_farm(farm_id: int, user: User, db: Session) -> Farm:
    farm = db.get(Farm, farm_id)
    if farm is None or farm.user_id != user.id:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED, summary="Save a farm")
def create_farm(payload: FarmCreate, user: CurrentUser, db: DatabaseSession) -> Farm:
    """Create a farm belonging only to the authenticated user."""
    farm = Farm(user_id=user.id, **payload.model_dump())
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm


@router.get("", response_model=list[FarmResponse], summary="List my farms")
def list_farms(user: CurrentUser, db: DatabaseSession) -> list[Farm]:
    return list(db.scalars(select(Farm).where(Farm.user_id == user.id).order_by(Farm.created_at.desc())))


@router.put("/{farm_id}", response_model=FarmResponse, summary="Update a saved farm")
def update_farm(farm_id: int, payload: FarmUpdate, user: CurrentUser, db: DatabaseSession) -> Farm:
    farm = owned_farm(farm_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(farm, field, value)
    db.commit()
    db.refresh(farm)
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a saved farm")
def delete_farm(farm_id: int, user: CurrentUser, db: DatabaseSession) -> None:
    db.delete(owned_farm(farm_id, user, db))
    db.commit()
