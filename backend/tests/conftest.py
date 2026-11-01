"""Pytest fixtures for API and database testing."""

import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as fastapi_app
from app.database.session import engine, async_session_factory, Base
from app import models
from app.database.seed import seed_database


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Ensures database tables are created and baseline records seeded for tests."""
    async def _init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_session_factory() as session:
            await seed_database(session)
    asyncio.run(_init())


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Synchronous test client for endpoint assertions with explicit mock engine for hermetic testing."""
    return TestClient(fastapi_app, headers={"X-OCR-Engine": "mock"})


@pytest.fixture
async def db_session() -> AsyncSession:
    """Async session fixture for repository tests."""
    async with async_session_factory() as session:
        yield session
