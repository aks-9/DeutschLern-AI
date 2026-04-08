"""Coach routes: scenario selector, start session, send message."""

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import CoachSession, CoachMessage, User
from app.services import ai_service

router = APIRouter(prefix="/coach", tags=["coach"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", include_in_schema=False)
async def coach_home(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Render the scenario selector page.

    :param request: The incoming FastAPI request.
    :param current_user: The authenticated user from the JWT cookie.
    :return: TemplateResponse rendering coach/chat.html with no active session.
    """
    return templates.TemplateResponse(
        request,
        "coach/chat.html",
        {"user": current_user, "session_id": None, "messages": []},
    ) # using session_id as a switch: if None → show scenario picker, if a number → show the chat


@router.post("/start", include_in_schema=False)
async def start_session(
    request: Request,
    scenario: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new coach session and generate the AI's opening message.

    :param request: The incoming FastAPI request.
    :param scenario: The selected scenario key from the form.
    :param current_user: The authenticated user from the JWT cookie.
    :param db: Async database session injected by FastAPI.
    :return: TemplateResponse rendering coach/chat.html with the new session.
    """
    # 1. Save the new session to the database
    session = CoachSession(user_id=current_user.id, scenario=scenario)
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # 2. Build the system prompt and get the AI's opening message
    system_prompt = ai_service.build_coach_system_prompt(current_user.level, scenario)
    opening = ai_service.get_coach_reply([], system_prompt)

    # 3. Save the opening message to the database
    db.add(CoachMessage(session_id=session.id, role="assistant", content=opening))
    await db.commit()

    return templates.TemplateResponse(
        request,
        "coach/chat.html",
        {
            "user": current_user,
            "session_id": session.id,
            "scenario": scenario,
            "messages": [{"role": "assistant", "content": opening}],
        },
    )


@router.post("/message", include_in_schema=False)
async def send_message(
    request: Request,
    session_id: int = Form(...),
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save the user's message, get the AI reply, and return an HTMX partial.

    :param request: The incoming FastAPI request.
    :param session_id: The active CoachSession id from the form.
    :param content: The user's message text.
    :param current_user: The authenticated user from the JWT cookie.
    :param db: Async database session injected by FastAPI.
    :raises HTTPException: 404 if the session does not exist.
    :return: HTMLResponse with two new chat bubbles (user + assistant).
    """
    # 1. Load the session — 404 if it doesn't exist
    result = await db.execute(
        select(CoachSession).where(CoachSession.id == session_id)
    )
    coach_session = result.scalar_one_or_none()
    if coach_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")

    # 2. Save the user's message
    db.add(CoachMessage(session_id=session_id, role="user", content=content))
    await db.commit()

    # 3. Load full history to send to the AI
    history_result = await db.execute(
        select(CoachMessage)
        .where(CoachMessage.session_id == session_id)
        .order_by(CoachMessage.id)
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in history_result.scalars().all()
    ] # building full conversation history from DB, converting each row into a dict format for GPT-4o

    # 4. Get AI reply and save it
    system_prompt = ai_service.build_coach_system_prompt(
        current_user.level, coach_session.scenario
    )
    reply = ai_service.get_coach_reply(history, system_prompt)
    db.add(CoachMessage(session_id=session_id, role="assistant", content=reply))
    await db.commit()

    # 5. Return HTMX partial — two new chat bubbles
    return templates.TemplateResponse(
        request,
        "coach/partials/messages.html",
        {"user_message": content, "ai_reply": reply},
    ) # HTMX inject into the existing chat without a page reload
