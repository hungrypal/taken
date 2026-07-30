"""HTTP endpoints for account registration, login, and profile retrieval."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.user import User
from backend.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserCreate, UserResponse
from backend.services.auth import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from backend.utils.logger import logger


router = APIRouter(tags=["authentication"])
bearer_scheme = HTTPBearer(auto_error=False)
DatabaseSession = Annotated[Session, Depends(get_db)]


def authentication_error() -> HTTPException:
    """Build a consistent RFC 6750-style authentication error response."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DatabaseSession,
) -> User:
    """Resolve the bearer token to an active account for protected routes."""
    if credentials is None:
        raise authentication_error()
    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise authentication_error()

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise authentication_error()
    return user


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DatabaseSession,
) -> User | None:
    """Optionally resolve a bearer token without breaking public ML routes."""
    if credentials is None:
        return None
    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        return None
    user = db.get(User, user_id)
    return user if user and user.is_active else None


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Require an authenticated account with administrative authorization."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: DatabaseSession) -> User:
    """Register an account with a unique, normalized email address."""
    email = str(payload.email).lower()
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=email, full_name=payload.full_name, hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # The database constraint is the final guard under concurrent signups.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db.refresh(user)
    logger.info("authentication_signup user_id=%s", user.id)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    """Authenticate a user and issue a short-lived bearer token."""
    email = str(payload.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
        logger.warning("authentication_login_failed email=%s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = TokenResponse(
        access_token=create_access_token(user.id),
        expires_in=settings.access_token_expire_minutes * 60,
        refresh_token=create_refresh_token(user.id),
    )
    logger.info("authentication_login user_id=%s", user.id)
    # Keep access-token response backwards compatible while exposing refresh
    # token support in the dedicated exchange endpoint.
    return token


@router.post("/refresh", response_model=TokenResponse, summary="Exchange a refresh token")
def refresh_token(payload: RefreshRequest, db: DatabaseSession) -> TokenResponse:
    """Issue a new access token for an active refresh-token holder."""
    try:
        user_id = decode_refresh_token(payload.refresh_token)
    except InvalidTokenError:
        raise authentication_error()
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise authentication_error()
    logger.info("authentication_refresh user_id=%s", user.id)
    return TokenResponse(access_token=create_access_token(user.id), expires_in=settings.access_token_expire_minutes * 60)


@router.get("/profile", response_model=UserResponse)
def profile(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Return the profile for the user represented by the bearer token."""
    return current_user
