import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)

from app.database import Base, get_db
from app.dependencies.container import Container
from main import create_app


# Database fixtures
@pytest.fixture(scope="session")
def event_loop() -> Generator:
	"""Create an instance of the default event loop for the test session."""
	loop = asyncio.get_event_loop_policy().new_event_loop()
	yield loop
	loop.close()


@pytest.fixture
async def test_db_engine():
	"""Create a test database engine."""
	# Use in-memory SQLite for tests
	engine = create_async_engine(
		"sqlite+aiosqlite:///:memory:",
		echo=False,
		future=True,
	)

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)

	yield engine

	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.drop_all)

	await engine.dispose()


@pytest.fixture
async def test_db_session(
	test_db_engine,
) -> AsyncGenerator[AsyncSession, None]:
	"""Create a test database session."""
	async_session = async_sessionmaker(
		test_db_engine,
		class_=AsyncSession,
		expire_on_commit=False,
		autocommit=False,
		autoflush=False,
	)

	async with async_session() as session:
		yield session
		await session.rollback()


# Application fixtures
@pytest.fixture
def app_with_test_db(test_db_session):
	"""Create FastAPI app with test database."""
	app = create_app()

	async def override_get_db():
		yield test_db_session

	app.dependency_overrides[get_db] = override_get_db

	yield app

	app.dependency_overrides.clear()


@pytest.fixture
async def client(app_with_test_db) -> AsyncGenerator[AsyncClient, None]:
	"""Create async test client."""
	async with AsyncClient(
		transport=ASGITransport(app=app_with_test_db), base_url="http://test"
	) as ac:
		yield ac


# Container fixtures
@pytest.fixture
def container():
	"""Create dependency injection container."""
	return Container()


# Mock fixtures
@pytest.fixture
def mock_user_id():
	"""Generate a mock user ID."""
	return uuid4()


@pytest.fixture
def mock_user_email():
	"""Generate a mock user email."""
	return f"test_{uuid4().hex[:8]}@example.com"
