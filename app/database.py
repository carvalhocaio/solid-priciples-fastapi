"""
Database configuration and session management
Following Dependency Inversion Principle (DIP)
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# Create async engine
engine = create_async_engine(
	DATABASE_URL,
	echo=True,  # Set to False in production
	future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
	engine,
	class_=AsyncSession,
	expire_on_commit=False,
	autocommit=False,
	autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	"""
	Dependency function to get database session

	Yields:
		AsyncSession: Database session

	Following DIP: Controllers depend on this abstraction, not concrete database
	"""
	async with AsyncSessionLocal() as session:
		try:
			logger.debug("Database session created")
			yield session
			await session.commit()
			logger.debug("Database session committed")
		except Exception as e:
			await session.rollback()
			logger.error(f"Database session rolled back due to error: {e}")
			raise
		finally:
			await session.close()
			logger.debug("Database session closed")


async def init_db():
	"""
	Initialize database tables

	Creates all tables defined in Base metadata
	"""
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
		logger.info("Database tables created successfully")


async def close_db():
	"""
	Close database connections

	Should be called on application shutdown
	"""
	await engine.dispose()
	logger.info("Database connections closed")
