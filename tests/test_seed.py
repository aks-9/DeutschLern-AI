import pytest_asyncio
from sqlalchemy import select, text

from app.models import GrammarTopic
from tests.conftest import TestSessionLocal
from seed import seed

@pytest_asyncio.fixture(autouse=True)
async def clean_topics():
    """Delete all grammar_topics rows before each test."""
    async with TestSessionLocal() as session:
        await session.execute(text("DELETE FROM grammar_topics"))
        await session.commit()

async def test_seed_inserts_six_topics():
    """Seeding should insert exactly 6 grammar topics."""
    await seed(session_factory=TestSessionLocal)
    async with TestSessionLocal() as session:
        result = await session.execute(select(GrammarTopic))
        topics = result.scalars().all() #fetches every row as Python objects into a list

    assert len(topics) == 6


async def test_seed_topics_are_level_a1():
    """All seeded topics should have level A1 and correct titles."""
    await seed(session_factory=TestSessionLocal)

    async with TestSessionLocal() as session:
        result = await session.execute(select(GrammarTopic))
        topics = result.scalars().all()

    titles = [t.title for t in topics]
    levels = [t.level for t in topics]

    assert all(level == "A1" for level in levels)
    assert "Der, Die, Das — German Articles" in titles
    assert "Sein und Haben — To Be & To Have" in titles
    assert "Verben im Präsens — Present Tense Verbs" in titles

async def test_seed_duplicate_guard():
    """Running seed twice should not create duplicate topics."""
    await seed(session_factory=TestSessionLocal)
    await seed(session_factory=TestSessionLocal)

    async with TestSessionLocal() as session:
        result = await session.execute(select(GrammarTopic))
        topics = result.scalars().all()

    assert len(topics) == 6