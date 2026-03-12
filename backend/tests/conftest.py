import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app
from app.models import *  # noqa: F401, F403

# Use test database URL or fall back to SQLite for local dev
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./test.db",
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    mock_redis = AsyncMock()
    mock_redis.close = AsyncMock()
    with patch("app.core.redis.from_url", return_value=mock_redis):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


async def create_test_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "TestPassword123!",
    role: str = "influencer",
) -> dict:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "role": role,
        },
    )
    return response.json()


async def get_auth_header(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "TestPassword123!",
) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
