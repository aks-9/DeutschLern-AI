"""Theory routes: list all grammar topics and view a single topic."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import GrammarTopic, User


router = APIRouter(prefix="/theory", tags=["theory"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", include_in_schema=False)
async def theory_list(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Render a list of all grammar topics ordered by level and index.

    :param request: The incoming FastAPI request.
    :param current_user: The authenticated user from the JWT cookie.
    :param db: Async database session injected by FastAPI.
    :return: TemplateResponse rendering theory/list.html with all topics.
    """
    result = await db.execute(
        select(GrammarTopic).order_by(GrammarTopic.order_index)
    )
    topics = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "theory/list.html",
        {"user": current_user, "topics": topics},
    )

@router.get("/{topic_id}", include_in_schema=False)
async def theory_detail(
    topic_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Render the detail view for a single grammar topic.

    :param topic_id: Primary key of the GrammarTopic to display.
    :param request: The incoming FastAPI request.
    :param current_user: The authenticated user from the JWT cookie.
    :param db: Async database session injected by FastAPI.
    :raises HTTPException: 404 if topic_id does not exist.
    :return: TemplateResponse rendering theory/detail.html with topic and
             prev/next navigation ids.
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
    # Load all topics in order to build prev/next navigation
    all_result = await db.execute(
        select(GrammarTopic).order_by(GrammarTopic.order_index)
    )
    all_topics = all_result.scalars().all()
    ids = [t.id for t in all_topics]
    current_pos = ids.index(topic_id)
    prev_id = ids[current_pos - 1] if current_pos > 0 else None
    next_id = (
        ids[current_pos + 1] if current_pos < len(ids) - 1 else None
    )

    return templates.TemplateResponse(
        request,
        "theory/detail.html",
        {
            "user": current_user,
            "topic": topic,
            "prev_id": prev_id,
            "next_id": next_id,
        },
    )
