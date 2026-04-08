"""Tests for coach routes: GET /coach, POST /coach/start, POST /coach/message."""

import pytest_asyncio
from unittest.mock import patch
from sqlalchemy import select

from app.models import User, CoachSession, CoachMessage
from tests.conftest import TestSessionLocal

REGISTER_URL = "/auth/register"
LOGIN_URL    = "/auth/login"

VALID_USER = {
    "username": "coachuser",
    "email":    "coach@example.com",
    "password": "securepassword123",
}


async def register_and_login(client, user=VALID_USER):
    await client.post(REGISTER_URL, data=user)
    await client.post(LOGIN_URL, data={"email": user["email"], "password": user["password"]})


async def get_user_id(email):
    async with TestSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one().id


# -- GET /coach ----------------------------------------------------------------


async def test_coach_requires_auth(client):
    """GET /coach without a cookie must return 401."""
    response = await client.get("/coach")
    assert response.status_code == 401


async def test_coach_returns_200(client):
    """GET /coach when logged in must return 200."""
    await register_and_login(client)
    response = await client.get("/coach")
    assert response.status_code == 200

# checks the page actually renders something useful — two of the four scenario (chat topics) names must appear, so we don't accidentally ship a blank page
async def test_coach_page_shows_scenarios(client):
    """GET /coach must show at least two scenario options on the page."""
    await register_and_login(client)
    response = await client.get("/coach")
    text = response.text.lower()
    assert "supermarket" in text or "supermarkt" in text
    assert "free" in text or "frei" in text


# -- POST /coach/start ---------------------------------------------------------


async def test_start_requires_auth(client):
    """POST /coach/start without a cookie must return 401."""
    response = await client.post("/coach/start", data={"scenario": "free"})
    assert response.status_code == 401

# goes straight to the DB after the request and checks a CoachSession row was actually written with the right scenario. It proves data was persisted, not just returned
async def test_start_creates_session_in_db(client):
    """POST /coach/start must create a CoachSession row in the database."""
    await register_and_login(client)
    user_id = await get_user_id(VALID_USER["email"])
    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Hallo!"):
        await client.post("/coach/start", data={"scenario": "free"})

    async with TestSessionLocal() as session:
        result = await session.execute(
            select(CoachSession).where(CoachSession.user_id == user_id)
        )
        sessions = result.scalars().all()
    assert len(sessions) == 1
    assert sessions[0].scenario == "free"


async def test_start_saves_opening_message(client):
    """POST /coach/start must save the AI's opening message as an assistant message."""
    await register_and_login(client)
    user_id = await get_user_id(VALID_USER["email"])
    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Willkommen!"):
        await client.post("/coach/start", data={"scenario": "supermarket"})

    async with TestSessionLocal() as session:
        result = await session.execute(select(CoachMessage))
        messages = result.scalars().all()
    assert len(messages) == 1
    assert messages[0].role == "assistant"
    assert "Willkommen!" in messages[0].content


async def test_start_renders_chat_page(client):
    """POST /coach/start must return 200 and render the opening message in HTML."""
    await register_and_login(client)
    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Guten Tag!"):
        response = await client.post("/coach/start", data={"scenario": "free"})
    assert response.status_code == 200
    assert "Guten Tag!" in response.text


# -- POST /coach/message -------------------------------------------------------


async def test_message_requires_auth(client):
    """POST /coach/message without a cookie must return 401."""
    response = await client.post(
        "/coach/message", data={"session_id": 1, "content": "Hallo"}
    )
    assert response.status_code == 401


async def test_message_saves_user_and_ai_reply(client):
    """POST /coach/message must save the user message and AI reply to the DB."""
    await register_and_login(client)
    user_id = await get_user_id(VALID_USER["email"])

    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Hallo!"):
        await client.post("/coach/start", data={"scenario": "free"})

    async with TestSessionLocal() as session:
        result = await session.execute(
            select(CoachSession).where(CoachSession.user_id == user_id)
        )
        session_id = result.scalar_one().id

    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Das ist gut!"):
        response = await client.post(
            "/coach/message",
            data={"session_id": session_id, "content": "Ich lerne Deutsch."},
        )
    assert response.status_code == 200

    async with TestSessionLocal() as session:
        result = await session.execute(
            select(CoachMessage)
            .where(CoachMessage.session_id == session_id)
            .order_by(CoachMessage.id)
        )
        messages = result.scalars().all()
    # opening message + user message + AI reply = 3 total
    assert len(messages) == 3
    assert messages[1].role == "user"
    assert messages[1].content == "Ich lerne Deutsch."
    assert messages[2].role == "assistant"
    assert messages[2].content == "Das ist gut!"


async def test_message_returns_ai_reply_in_html(client):
    """POST /coach/message must return an HTMX partial containing the AI reply."""
    await register_and_login(client)
    user_id = await get_user_id(VALID_USER["email"])

    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Sehr gut!"):
        await client.post("/coach/start", data={"scenario": "free"})

    async with TestSessionLocal() as session:
        result = await session.execute(
            select(CoachSession).where(CoachSession.user_id == user_id)
        )
        session_id = result.scalar_one().id

    with patch("app.routers.coach.ai_service.get_coach_reply", return_value="Wunderbar!"):
        response = await client.post(
            "/coach/message",
            data={"session_id": session_id, "content": "Guten Morgen!"},
        )
    assert "Wunderbar!" in response.text


async def test_message_invalid_session_returns_404(client):
    """POST /coach/message with a non-existent session_id must return 404."""
    await register_and_login(client)
    response = await client.post(
        "/coach/message",
        data={"session_id": 99999, "content": "Hallo"},
    )
    assert response.status_code == 404
