"""Vocabulary routes: list, save, and delete user vocabulary entries."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, VocabularyEntry

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
