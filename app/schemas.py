"""Pydantic schemas for request and response validation."""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema for user registration form data."""

    email: EmailStr
    username: str
    password: str


class UserRead(BaseModel):
    """Schema for returning user data in responses (no password)."""

    id: int
    email: EmailStr
    username: str
    level: str

    class Config:
        """Enable ORM mode so SQLAlchemy models can be serialised."""

        from_attributes = True
