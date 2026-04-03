"""Tests for exercise routes: GET /exercises/{topic_id} and POST /exercises/check."""

import pytest_asyncio
from unittest.mock import patch

from app.models import GrammarTopic
from tests.conftest import TestSessionLocal

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"

VALID_USER = {
    "username": "exerciseuser",
    "email": "exercise@example.com",
    "password": "securepassword123",
}

FAKE_EXERCISE = {
    "sentence": "Ich ___ ein Student.",
    "blank_word": "bin",
    "hint": "verb to be, first person",
    "explanation": "'bin' is the ich-form of sein.",
}

FAKE_GRADE_CORRECT = {
    "correct": True,
    "score": 1.0,
    "feedback": "Perfekt! 'bin' is correct.",
}

FAKE_GRADE_WRONG = {
    "correct": False,
    "score": 0.0,
    "feedback": "Not quite — 'bist' is the du-form of sein.",
}


# -- Fixtures ------------------------------------------------------------------


@pytest_asyncio.fixture()
async def seeded_topic():
    """Insert one A1 grammar topic and return it."""
    topic = GrammarTopic(
        order_index=1,
        title="Articles",
        level="A1",
        content="<p>Der, Die, Das content here.</p>",
    )
    async with TestSessionLocal() as session:
        session.add(topic)
        await session.commit()
        await session.refresh(topic) #forces SQLAlchemy to read the id back from the database so we can use topic.id in our URLs
    return topic


# -- Helpers -------------------------------------------------------------------


async def register_and_login(client):
    """Register then log in; session cookie is stored on the client.

    :param client: The httpx AsyncClient fixture.
    """
    await client.post(REGISTER_URL, data=VALID_USER)
    await client.post(
        LOGIN_URL,
        data={
            "email": VALID_USER["email"],
            "password": VALID_USER["password"],
        },
    )


# -- GET /exercises/{topic_id} ------------------------------------------------



async def test_exercise_page_requires_auth(client, seeded_topic):
    """GET /exercises/{id} without a cookie must return 401."""
    response = await client.get(f"/exercises/{seeded_topic.id}")
    assert response.status_code == 401



async def test_exercise_page_returns_200(client, seeded_topic):
    """GET /exercises/{id} when logged in must return 200."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.generate_exercise", #
        return_value=FAKE_EXERCISE,
    ):
        response = await client.get(f"/exercises/{seeded_topic.id}")
    assert response.status_code == 200

    # patch("app.routers.exercises.generate_exercise", ...) patches the function where it is used (in the router), not where it is defined (in ai_service). This is the correct way to mock in Python.



async def test_exercise_page_shows_sentence(client, seeded_topic):
    """GET /exercises/{id} must render the exercise sentence on the page."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.generate_exercise",
        return_value=FAKE_EXERCISE,
    ):
        response = await client.get(f"/exercises/{seeded_topic.id}")
    assert "Ich ___ ein Student." in response.text



async def test_exercise_page_shows_hint(client, seeded_topic):
    """GET /exercises/{id} must render the hint text on the page."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.generate_exercise",
        return_value=FAKE_EXERCISE,
    ):
        response = await client.get(f"/exercises/{seeded_topic.id}")
    assert "verb to be, first person" in response.text


# -- POST /exercises/check ----------------------------------------------------



async def test_check_requires_auth(client, seeded_topic):
    """POST /exercises/check without a cookie must return 401."""
    response = await client.post(
        "/exercises/check",
        data={
            "sentence": FAKE_EXERCISE["sentence"],
            "blank_word": FAKE_EXERCISE["blank_word"],
            "user_answer": "bin",
            "topic_id": str(seeded_topic.id),
        },
    )
    assert response.status_code == 401



async def test_check_correct_answer_shows_feedback(client, seeded_topic):
    """POST /exercises/check with correct answer must return feedback HTML."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.grade_answer",
        return_value=FAKE_GRADE_CORRECT,
    ):
        response = await client.post(
            "/exercises/check",
            data={
                "sentence": FAKE_EXERCISE["sentence"],
                "blank_word": FAKE_EXERCISE["blank_word"],
                "user_answer": "bin",
                "topic_id": str(seeded_topic.id),
            },
        )
    assert response.status_code == 200
    assert "Perfekt!" in response.text



async def test_check_wrong_answer_shows_feedback(client, seeded_topic):
    """POST /exercises/check with wrong answer must return feedback HTML."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.grade_answer",
        return_value=FAKE_GRADE_WRONG,
    ):
        response = await client.post(
            "/exercises/check",
            data={
                "sentence": FAKE_EXERCISE["sentence"],
                "blank_word": FAKE_EXERCISE["blank_word"],
                "user_answer": "bist",
                "topic_id": str(seeded_topic.id),
            },
        )
        #the data dictionary sends application/x-www-form-urlencoded, matching how HTML forms work and how our Form(...) params will receive the data.

    assert response.status_code == 200
    assert "Not quite" in response.text
