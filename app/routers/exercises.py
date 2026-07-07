"""Exercise routes: fill-in-the-blank generation and answer grading."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import GrammarTopic, User, Exercise, ExerciseAttempt
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

    try:
        exercise = generate_exercise(topic.title, current_user.level)
    except Exception:
        exercise = None  # template shows an error card instead of the exercise

    exercise_id = None
    if exercise is not None:
        # Persist the exercise so grading can look it up server-side
        # and attempts can be linked back to the topic
        exercise_row = Exercise(
            topic_id=topic.id,
            level=current_user.level,
            type="fill_blank",
            question_data=exercise,
        )
        db.add(exercise_row)
        await db.commit()
        await db.refresh(exercise_row)
        exercise_id = exercise_row.id

    return templates.TemplateResponse(
        request,
        "exercises/fill_blank.html",
        {
            "user": current_user,
            "topic": topic,
            "exercise": exercise,
            "exercise_id": exercise_id,
        },
    )


@router.post("/check", response_class=HTMLResponse)
async def check_answer(
    request: Request,
    exercise_id: int = Form(...),
    user_answer: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grade the user's answer and return an HTMX feedback partial.

    The exercise (sentence and correct answer) is loaded server-side by
    id — the browser never sees or submits the correct answer.

    :param request: The incoming FastAPI request.
    :param exercise_id: Primary key of the persisted Exercise to grade against.
    :param user_answer: The answer submitted by the user.
    :param db: Async database session injected by FastAPI.
    :param current_user: The authenticated user from the JWT cookie.
    :raises HTTPException: 404 if the exercise does not exist.
    :return: TemplateResponse rendering exercises/partials/feedback.html.
    """
    result_db = await db.execute(
        select(Exercise).where(Exercise.id == exercise_id)
    )
    exercise = result_db.scalar_one_or_none()
    if exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found.",
        )

    sentence = exercise.question_data["sentence"]
    blank_word = exercise.question_data["blank_word"]

    try:
        result = grade_answer(
            sentence=sentence,
            blank_word=blank_word,
            user_answer=user_answer,
            level=current_user.level,
        )
    except Exception:
        # Grading failed — show a retry message, save no attempt
        return templates.TemplateResponse(
            request,
            "exercises/partials/feedback.html",
            {
                "result": None,
                "blank_word": blank_word,
                "topic_id": exercise.topic_id,
            },
        )

    attempt = ExerciseAttempt(
        user_id=current_user.id,
        exercise_id=exercise.id,
        user_answer=user_answer,
        score=result.get("score", 0.0),
        feedback=result.get("feedback", ""),
    )
    db.add(attempt)
    await db.commit()

    return templates.TemplateResponse(
        request,
        "exercises/partials/feedback.html",
        {
            "result": result,
            "blank_word": blank_word,
            "topic_id": exercise.topic_id,
        },
    )
