"""Authentication routes: register, login, logout."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a plain-text password using bcrypt.

    :param plain: The plain-text password from the registration form.
    :return: A bcrypt-hashed password string safe to store in the DB.
    """
    return pwd_context.hash(plain)


def create_access_token(user_id: int) -> str:
    """Create a signed JWT access token for the given user.

    :param user_id: The primary key of the authenticated user.
    :return: A signed JWT string to be stored in an httponly cookie.
    """
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Register a new user  from the HTML form.

    Checks for duplicate email, hashes the password, saves the user
    to the database, then redirects to the login page.

    :param username: Desired display name from the registration form.
    :param email: Email address from the registration form.
    :param password: Plain-text password from the registration form.
    :param db: Async database session injected by FastAPI.
    :raises HTTPException: 400 if the email is already registered.
    :return: RedirectResponse to the login page on success.
    """
    # Check for duplicate email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # Hash password and create user
    new_user = User(
        email= email,
        username= username,
        password_hash=hash_password(password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return RedirectResponse(
        url="/auth/login", status_code=status.HTTP_302_FOUND
    )


@router.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Authenticate a user and issue a JWT cookie.

    Looks up the user by email, verifies the bcrypt password, mints a
    JWT, and stores it in an httponly cookie before redirecting to the
    dashboard.

    :param email: Submitted login email from the HTML form.
    :param password: Submitted plain-text password from the HTML form.
    :param db: Async database session injected by FastAPI.
    :raises HTTPException: 401 if email not found or password is wrong.
    :return: RedirectResponse to /dashboard with access_token cookie set.
    """
    # Look up user by email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    # Same error for wrong email or wrong password — never reveal which half failed
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token(user.id)

    response = RedirectResponse(
        url="/dashboard", status_code=status.HTTP_302_FOUND
    )
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,   # JS cannot read this cookie — prevents XSS token theft
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # minutes → seconds
        samesite="lax",  # blocks cross-site form submissions (CSRF protection)
    )
    return response

@router.get("/register" , include_in_schema=False) #hides this route from the Swagger docs.
async def register_form(request: Request):
    """
    Serve the registration HTML form.
    :param request: The incoming FastAPI request (needed by Jinja2Templates).
    :return: TemplateResponse rendering auth/register.html
    """
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request}
    )

@router.get("/login", include_in_schema=False)
async def login_form(request: Request):
    """
    Serve the login HTML form
    :param request: The incoming FastAPI request (needed by Jinja2Templates).
    :return: TemplateResponse redering auth/login.html
    """
    return templates.TemplateResponse(
        "auth/login.html", {"request": request}
    )

@router.get("/logout", include_in_schema=False)
async def logout():
    """
    Log the user out by deleting the JWT cookie.
    :return: RedirectResponse to /auth/login with the access_token cookie deleted.
    """
    response = RedirectResponse(
        url = "/auth/login", status_code=status.HTTP_302_FOUND
    )
    response.delete_cookie("access_token")
    return response