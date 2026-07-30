"""Password and JWT operations kept outside HTTP route handlers."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.config import settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidTokenError(Exception):
    """Raised when a JWT cannot identify an authenticated user."""


def hash_password(password: str) -> str:
    """Return a bcrypt hash; plaintext passwords are never persisted."""
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validate a plaintext password against its stored bcrypt hash."""
    return password_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create a short-lived JWT containing only the account identifier."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at, "type": "access"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(user_id: int) -> str:
    """Create a longer-lived refresh JWT; it cannot access protected routes."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at, "type": "refresh"},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str, expected_type: str) -> int:
    """Return the authenticated user ID or raise ``InvalidTokenError``."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        subject = payload.get("sub")
        if payload.get("type") != expected_type or not subject:
            raise InvalidTokenError
        return int(subject)
    except (JWTError, TypeError, ValueError) as exc:
        raise InvalidTokenError from exc


def decode_access_token(token: str) -> int:
    """Decode an access token only."""
    return decode_token(token, "access")


def decode_refresh_token(token: str) -> int:
    """Decode a refresh token only."""
    return decode_token(token, "refresh")
