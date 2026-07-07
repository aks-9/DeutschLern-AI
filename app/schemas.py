"""Pydantic schemas for request and response validation."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration form data."""

    email: EmailStr
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    """Schema for returning user data in responses (no password)."""

    id: int
    email: EmailStr
    username: str
    level: str

    model_config = ConfigDict(from_attributes=True)
