"""Exercise routes: fill-in-the-blank generation and answer grading."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import GrammarTopic, User
from app.services.ai_service import generate_exercise, grade_answer

router = APIRouter(prefix="/exercises", tags=["exercises"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/{topic_id}", response_class=HTMLResponse)
async def exercise_page(
    topic_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Render a fill-in-the-blank exercise for the given topic.

    :param topic_id: Primary key of the GrammarTopic.
    :param request: The incoming FastAPI request.
    :param db: Async database session injected by FastAPI.
    :param current_user: The authenticated user from the JWT cookie.
    :raises HTTPException: 404 if the topic does not exist.
    :return: TemplateResponse rendering exercises/fill_blank.html.
    """
    result = await db.execute(
        select(GrammarTopic).where(GrammarTopic.id == topic_id)
    )
    topic = result.scalar_one_or_none()
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found.",
        )

    exercise = generate_exercise(topic.title, current_user.level)

    return templates.TemplateResponse(
        request,
        "exercises/fill_blank.html",
        {"user": current_user, "topic": topic, "exercise": exercise},
    )


@router.post("/check", response_class=HTMLResponse)
async def check_answer(
    request: Request,
    sentence: str = Form(...),
    blank_word: str = Form(...),
    user_answer: str = Form(...),
    topic_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grade the user's answer and return an HTMX feedback partial.

    :param request: The incoming FastAPI request.
    :param sentence: The exercise sentence with ____ as the blank.
    :param blank_word: The correct answer word.
    :param user_answer: The answer submitted by the user.
    :param topic_id: Primary key of the grammar topic (for retry link).
    :param db: Async database session injected by FastAPI.
    :param current_user: The authenticated user from the JWT cookie.
    :return: TemplateResponse rendering exercises/partials/feedback.html.
    """
    result = grade_answer(
        sentence=sentence,
        blank_word=blank_word,
        user_answer=user_answer,
        level=current_user.level,
    )

    return templates.TemplateResponse(
        request,
        "exercises/partials/feedback.html",
        {
            "result": result,
            "blank_word": blank_word,
            "topic_id": topic_id,
        },
    )
