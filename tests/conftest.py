"""Shared pytest fixtures for the DeutschLern AI test suite."""

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import get_db, Base
from app.main import app
from config import settings

# Derive test DB URL from the configured DATABASE_URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "/deutschlern_ai", "/deutschlern_ai_test"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once before the test session; drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_vocabulary():
    """Delete all rows from vocabulary_entries before each test."""
    async with test_engine.begin() as conn:
        await conn.execute(text("DELETE FROM vocabulary_entries"))


@pytest_asyncio.fixture(autouse=True)
async def clean_users():
    """Delete all rows from the users table before each test.

    Uses TRUNCATE CASCADE so that child rows in vocabulary_entries,
    coach_sessions, etc. are removed automatically, regardless of the
    order in which autouse fixtures run.
    """
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE users CASCADE"))

@pytest_asyncio.fixture(autouse=True)
async def clean_topics():
    """Delete all rows from the grammar_topics table before each test."""
    async with test_engine.begin() as conn:
        await conn.execute(text("DELETE FROM grammar_topics"))

@pytest_asyncio.fixture()
async def client():
    """Return an httpx AsyncClient wired to the FastAPI app and test DB."""
    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
