"""Tests for exercise routes: GET /exercises/{topic_id} and POST /exercises/check."""

import pytest_asyncio
from unittest.mock import patch
from sqlalchemy import select

from app.models import GrammarTopic, Exercise, ExerciseAttempt
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


@pytest_asyncio.fixture()
async def seeded_exercise(seeded_topic):
    """Insert one cached exercise row for the seeded topic and return it."""
    exercise = Exercise(
        topic_id=seeded_topic.id,
        level="A1",
        type="fill_blank",
        question_data=FAKE_EXERCISE,
    )
    async with TestSessionLocal() as session:
        session.add(exercise)
        await session.commit()
        await session.refresh(exercise)
    return exercise


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



async def test_exercise_page_survives_ai_failure(client, seeded_topic):
    """GET /exercises/{id} must return 200 with an error message when the AI call fails."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.generate_exercise",
        side_effect=Exception("OpenAI is down"),
    ):
        response = await client.get(f"/exercises/{seeded_topic.id}")
    assert response.status_code == 200
    assert "could not be generated" in response.text.lower()


# -- Exercise persistence (GAPS #5) --------------------------------------------


async def test_exercise_page_persists_exercise(client, seeded_topic):
    """GET /exercises/{id} must save the generated exercise to the DB."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.generate_exercise",
        return_value=FAKE_EXERCISE,
    ):
        await client.get(f"/exercises/{seeded_topic.id}")

    async with TestSessionLocal() as session:
        result = await session.execute(
            select(Exercise).where(Exercise.topic_id == seeded_topic.id)
        )
        exercises = result.scalars().all()
    assert len(exercises) == 1
    assert exercises[0].type == "fill_blank"
    assert exercises[0].question_data["blank_word"] == "bin"


async def test_exercise_page_does_not_leak_answer(client, seeded_topic):
    """GET /exercises/{id} must not embed the correct answer in the HTML (GAPS #6)."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.generate_exercise",
        return_value=FAKE_EXERCISE,
    ):
        response = await client.get(f"/exercises/{seeded_topic.id}")
    assert 'name="blank_word"' not in response.text
    assert "bin" not in response.text  # the answer itself must not appear anywhere


# -- POST /exercises/check ----------------------------------------------------



async def test_check_requires_auth(client, seeded_exercise):
    """POST /exercises/check without a cookie must return 401."""
    response = await client.post(
        "/exercises/check",
        data={"exercise_id": str(seeded_exercise.id), "user_answer": "bin"},
    )
    assert response.status_code == 401



async def test_check_correct_answer_shows_feedback(client, seeded_exercise):
    """POST /exercises/check with correct answer must return feedback HTML."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.grade_answer",
        return_value=FAKE_GRADE_CORRECT,
    ):
        response = await client.post(
            "/exercises/check",
            data={"exercise_id": str(seeded_exercise.id), "user_answer": "bin"},
        )
    assert response.status_code == 200
    assert "Perfekt!" in response.text



async def test_check_wrong_answer_shows_feedback(client, seeded_exercise):
    """POST /exercises/check with wrong answer must return feedback HTML."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.grade_answer",
        return_value=FAKE_GRADE_WRONG,
    ):
        response = await client.post(
            "/exercises/check",
            data={"exercise_id": str(seeded_exercise.id), "user_answer": "bist"},
        )
        #the data dictionary sends application/x-www-form-urlencoded, matching how HTML forms work and how our Form(...) params will receive the data.

    assert response.status_code == 200
    assert "Not quite" in response.text



async def test_check_saves_attempt_with_exercise_id(client, seeded_exercise):
    """POST /exercises/check must save an ExerciseAttempt linked to the exercise."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.grade_answer",
        return_value=FAKE_GRADE_CORRECT,
    ):
        await client.post(
            "/exercises/check",
            data={"exercise_id": str(seeded_exercise.id), "user_answer": "bin"},
        )

    async with TestSessionLocal() as session:
        result = await session.execute(select(ExerciseAttempt))
        attempts = result.scalars().all()
    assert len(attempts) == 1
    assert attempts[0].exercise_id == seeded_exercise.id
    assert attempts[0].score == 1.0



async def test_check_unknown_exercise_returns_404(client, seeded_topic):
    """POST /exercises/check with a non-existent exercise_id must return 404."""
    await register_and_login(client)
    response = await client.post(
        "/exercises/check",
        data={"exercise_id": "99999", "user_answer": "bin"},
    )
    assert response.status_code == 404



async def test_check_survives_ai_failure(client, seeded_exercise):
    """POST /exercises/check must return 200 with a retry message when grading fails."""
    await register_and_login(client)
    with patch(
        "app.routers.exercises.grade_answer",
        side_effect=Exception("OpenAI is down"),
    ):
        response = await client.post(
            "/exercises/check",
            data={"exercise_id": str(seeded_exercise.id), "user_answer": "bin"},
        )
    assert response.status_code == 200
    assert "could not be graded" in response.text.lower()
