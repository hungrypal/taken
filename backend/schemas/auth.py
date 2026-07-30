"""Authentication API validation and response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload accepted when a user creates an account."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    model_config = ConfigDict(json_schema_extra={"example": {"email": "farmer@example.com", "password": "SafePassword123!", "full_name": "Asha Patel"}})


class LoginRequest(BaseModel):
    """Credentials accepted by the login endpoint."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    model_config = ConfigDict(json_schema_extra={"example": {"email": "farmer@example.com", "password": "SafePassword123!"}})


class TokenResponse(BaseModel):
    """JWT access token returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class RefreshRequest(BaseModel):
    """Refresh token exchange request."""

    refresh_token: str = Field(min_length=20)


class UserResponse(BaseModel):
    """Safe public representation of an account (never includes a password)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime
