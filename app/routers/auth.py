"""Authentication routes: register, login, logout."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt.

    Args:
        plain: The plain-text password from the registration form.

    Returns:
        A bcrypt-hashed password string safe to store in the DB.
    """
    return pwd_context.hash(plain)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user.

    Checks for duplicate email, hashes the password, saves the user
    to the database, then redirects to the login page.

    Args:
        user_in: Validated registration data from the request body.
        db: Async database session injected by FastAPI.

    Raises:
        HTTPException: 400 if the email is already registered.

    Returns:
        RedirectResponse to the login page on success.
    """
    # Check for duplicate email
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # Hash password and create user
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=hash_password(user_in.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return RedirectResponse(
        url="/auth/login", status_code=status.HTTP_302_FOUND
    )
