"""Tests for theory routes: GET /theory and GET /theory/{topic_id}."""

import pytest
import pytest_asyncio

from app.models import GrammarTopic
from tests.conftest import TestSessionLocal

THEORY_LIST_URL = "/theory"
REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"

VALID_USER = {
    "username": "theoryuser",
    "email": "theory@example.com",
    "password": "securepassword123",
}


# ── Fixtures ────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture()
async def seeded_topics():
    """Insert 3 test grammar topics and return them in order."""
    topics = [
        GrammarTopic(
            order_index=1,
            title="Articles",
            level="A1",
            content="<p>Der, Die, Das content here.</p>",
        ),
        GrammarTopic(
            order_index=2,
            title="Verbs",
            level="A1",
            content="<p>Present tense verb content here.</p>",
        ),
        GrammarTopic(
            order_index=3,
            title="Sentence Structure",
            level="A1",
            content="<p>V2 rule content here.</p>",
        ),
    ]
    async with TestSessionLocal() as session:
        session.add_all(topics)
        await session.commit()
        for t in topics:
            await session.refresh(t)
    return topics


# ── Helpers ─────────────────────────────────────────────────────────────────────

async def register_and_login(client):
    """Register then log in; cookie is stored on the client."""
    await client.post(REGISTER_URL, data=VALID_USER)
    await client.post(
        LOGIN_URL,
        data={
            "email": VALID_USER["email"],
            "password": VALID_USER["password"],
        },
    )


# ── List route ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_theory_list_requires_auth(client):
    """GET /theory without a cookie should return 401."""
    response = await client.get(THEORY_LIST_URL)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_theory_list_returns_200(client, seeded_topics):
    """GET /theory when logged in should return 200."""
    await register_and_login(client)
    response = await client.get(THEORY_LIST_URL)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_theory_list_shows_topic_titles(client, seeded_topics):
    """GET /theory should render each topic title on the page."""
    await register_and_login(client)
    response = await client.get(THEORY_LIST_URL)
    assert "Articles" in response.text
    assert "Verbs" in response.text
    assert "Sentence Structure" in response.text


# ── Detail route ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_theory_detail_requires_auth(client, seeded_topics):
    """GET /theory/{id} without a cookie should return 401."""
    topic_id = seeded_topics[0].id
    response = await client.get(f"/theory/{topic_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_theory_detail_returns_200(client, seeded_topics):
    """GET /theory/{id} when logged in should return 200."""
    await register_and_login(client)
    topic_id = seeded_topics[0].id
    response = await client.get(f"/theory/{topic_id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_theory_detail_shows_content(client, seeded_topics):
    """GET /theory/{id} should render the topic title and content."""
    await register_and_login(client)
    topic = seeded_topics[1]
    response = await client.get(f"/theory/{topic.id}")
    assert topic.title in response.text
    assert "Present tense verb content here." in response.text


@pytest.mark.asyncio
async def test_theory_detail_404_for_unknown_id(client, seeded_topics):
    """GET /theory/9999 should return 404 when the topic does not exist."""
    await register_and_login(client)
    response = await client.get("/theory/9999")
    assert response.status_code == 404


# ── Prev / Next navigation ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_theory_detail_first_topic_has_no_prev(client, seeded_topics):
    """The first topic should not render a Previous navigation link."""
    await register_and_login(client)
    first_id = seeded_topics[0].id
    response = await client.get(f"/theory/{first_id}")
    assert "Previous" not in response.text


@pytest.mark.asyncio
async def test_theory_detail_last_topic_has_no_next(client, seeded_topics):
    """The last topic should not render a Next navigation link."""
    await register_and_login(client)
    last_id = seeded_topics[-1].id
    response = await client.get(f"/theory/{last_id}")
    # Check for the link text, not the word "Next" which also appears in a
    # HTML comment (<!-- Prev / Next navigation -->) that is always rendered.
    assert "Next &rarr;" not in response.text


@pytest.mark.asyncio
async def test_theory_detail_middle_topic_has_both_nav(client, seeded_topics):
    """A middle topic should render both Previous and Next navigation links."""
    await register_and_login(client)
    middle_id = seeded_topics[1].id
    response = await client.get(f"/theory/{middle_id}")
    assert "Previous" in response.text
    assert "Next &rarr;" in response.text
