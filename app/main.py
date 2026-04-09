from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import User, VocabularyEntry, ExerciseAttempt, CoachSession
from app.dependencies import get_current_user
from app.database import get_db
from fastapi.templating import Jinja2Templates
from app.routers import auth, theory, exercises, vocabulary, coach

app = FastAPI(title="DeutschLern AI")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(theory.router)
app.include_router(exercises.router)
app.include_router(vocabulary.router)
app.include_router(coach.router)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect the root URL to the dashboard."""
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard", include_in_schema=False)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Render the user dashboard

    :param request: The incoming FastAPI request.
    :param current_user: The authenticated user from the JWT cookie
    :param db: Async database session injected by FastAPI.
    :return: TemplateResponse rendering dashboard.html with basic user data
    """
    result = await db.execute(
        select(func.count()).where(VocabularyEntry.user_id == current_user.id)
    )
    word_count = result.scalar()

    result = await db.execute(
        select(func.count()).where(ExerciseAttempt.user_id == current_user.id)
    )
    exercises_done = result.scalar()

    result = await db.execute(
        select(func.count()).where(CoachSession.user_id == current_user.id)
    )
    session_count = result.scalar()

    result = await db.execute(
        select(CoachSession.started_at)
        .where(CoachSession.user_id == current_user.id)
        .order_by(CoachSession.started_at.desc())
        .limit(1)
    )
    last_session = result.scalar()

    return templates.TemplateResponse(
        request, "dashboard.html", {
            "user": current_user,
            "word_count": word_count,
            "exercises_done": exercises_done,
            "session_count": session_count,
            "last_session": last_session,
        }
    )

