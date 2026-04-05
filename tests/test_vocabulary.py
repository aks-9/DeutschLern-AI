"""Tests for vocabulary routes: GET /vocabulary."""

import pytest_asyncio
from sqlalchemy import select

from app.models import User, VocabularyEntry
from tests.conftest import TestSessionLocal

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"

VALID_USER = {
    "username": "vocabuser",
    "email": "vocab@example.com",
    "password": "securepassword123",
}

OTHER_USER = {
    "username": "otheruser",
    "email": "other@example.com",
    "password": "securepassword123",
}


# -- Helpers -------------------------------------------------------------------


async def register_and_login(client, user=VALID_USER):
    """Register then log in; session cookie is stored on the client.

    :param client: The httpx AsyncClient fixture.
    :param user: Dict with username, email, password fields.
    """
    await client.post(REGISTER_URL, data=user)
    await client.post(
        LOGIN_URL,
        data={"email": user["email"], "password": user["password"]},
    )


async def get_user_id(email):
    """Return the id of the user with the given email from the test DB.

    :param email: The email address to look up.
    :return: The integer user id.
    """
    async with TestSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one().id


# -- Fixtures ------------------------------------------------------------------


@pytest_asyncio.fixture()
async def seeded_vocab(client):
    """Register/login as VALID_USER and insert two vocab entries.

    :param client: The httpx AsyncClient fixture.
    :return: The list of inserted VocabularyEntry objects.
    """
    await register_and_login(client)
    user_id = await get_user_id(VALID_USER["email"])
    entries = [
        VocabularyEntry(
            user_id=user_id,
            word="der Hund",
            meaning="the dog",
            gender="masculine",
            level="A1",
        ),
        VocabularyEntry(
            user_id=user_id,
            word="die Katze",
            meaning="the cat",
            gender="feminine",
            level="A1",
        ),
    ]
    async with TestSessionLocal() as session:
        session.add_all(entries)
        await session.commit()
    return entries


# -- GET /vocabulary -----------------------------------------------------------


async def test_vocabulary_requires_auth(client):
    """GET /vocabulary without a cookie must return 401."""
    response = await client.get("/vocabulary")
    assert response.status_code == 401


async def test_vocabulary_returns_200(client):
    """GET /vocabulary when logged in must return 200."""
    await register_and_login(client)
    response = await client.get("/vocabulary")
    assert response.status_code == 200


async def test_vocabulary_empty_state(client):
    """GET /vocabulary with no saved words must show an empty-state message."""
    await register_and_login(client)
    response = await client.get("/vocabulary")
    assert response.status_code == 200
    assert "no words" in response.text.lower() or "keine" in response.text.lower()


async def test_vocabulary_shows_word_and_meaning(client, seeded_vocab):
    """GET /vocabulary must render each saved word and its meaning."""
    response = await client.get("/vocabulary")
    assert "der Hund" in response.text
    assert "the dog" in response.text
    assert "die Katze" in response.text
    assert "the cat" in response.text


async def test_vocabulary_only_shows_own_words(client, seeded_vocab):
    """GET /vocabulary must not show words belonging to another user."""
    await client.post(REGISTER_URL, data=OTHER_USER)
    other_id = await get_user_id(OTHER_USER["email"])
    async with TestSessionLocal() as session:
        session.add(
            VocabularyEntry(
                user_id=other_id,
                word="das Buch",
                meaning="the book",
                level="A1",
            )
        )
        await session.commit()

    # client is still logged in as VALID_USER
    response = await client.get("/vocabulary")
    assert "das Buch" not in response.text
