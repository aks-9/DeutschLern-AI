"""Vocabulary routes: list, save, and delete user vocabulary entries."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, VocabularyEntry
from app.services import ai_service

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
async def vocabulary_list(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Render the vocabulary list page for the logged-in user.

    :param request: The incoming FastAPI request.
    :param current_user: The authenticated user from the JWT cookie.
    :param db: Async database session injected by FastAPI.
    :return: TemplateResponse rendering vocabulary/list.html with the
             user's saved words, ordered newest first.
    """
    result = await db.execute(
        select(VocabularyEntry)
        .where(VocabularyEntry.user_id == current_user.id)
        .order_by(VocabularyEntry.created_at.desc())
    )
    entries = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "vocabulary/list.html",
        {"user": current_user, "entries": entries},
    )


@router.post("/save")
async def vocabulary_save(
    word: str = Form(...),
    meaning: str = Form(...),
    level: str = Form("A1"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a new vocabulary word for the logged-in user."""
    try:
        example = ai_service.generate_example_sentence(word, level)
    except Exception:
        example = None

    entry = VocabularyEntry(
        user_id=current_user.id,
        word=word,
        meaning=meaning,
        level=level,
        example_sentence=example,
    )
    db.add(entry)
    await db.commit()

    return RedirectResponse(url="/vocabulary", status_code=303)


@router.delete("/{entry_id}")
async def vocabulary_delete(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(VocabularyEntry).where(VocabularyEntry.id == entry_id)
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Word not found")

    if entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your word")

    await db.delete(entry)
    await db.commit()
    return Response(status_code=200)
