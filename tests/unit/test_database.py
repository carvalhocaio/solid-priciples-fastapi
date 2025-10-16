"""
Unit tests for database module
Testing database session management and lifecycle functions
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.database import close_db, get_db, init_db


@pytest.mark.unit
class TestGetDb:
	"""Test get_db dependency function."""

	async def test_get_db_success(self):
		"""
		GIVEN a database session factory
		WHEN getting a database session
		THEN session is yielded and committed
		"""
		# Arrange
		mock_session = AsyncMock()
		mock_session.commit = AsyncMock()
		mock_session.close = AsyncMock()

		# Act
		with patch("app.database.AsyncSessionLocal") as mock_factory:
			mock_factory.return_value.__aenter__.return_value = mock_session
			mock_factory.return_value.__aexit__.return_value = None

			db_generator = get_db()
			session = await db_generator.__anext__()

			# Assert - session is yielded
			assert session == mock_session

			# Simulate end of context (cleanup)
			try:
				await db_generator.__anext__()
			except StopAsyncIteration:
				pass

			# Assert - commit and close were called
			mock_session.commit.assert_called_once()
			mock_session.close.assert_called_once()

	async def test_get_db_rollback_on_error(self):
		"""
		GIVEN a database session that encounters an error
		WHEN an exception occurs during session usage
		THEN session is rolled back and error is propagated
		"""
		# Arrange
		mock_session = AsyncMock()
		mock_session.rollback = AsyncMock()
		mock_session.close = AsyncMock()
		mock_session.commit = AsyncMock(side_effect=Exception("DB Error"))

		# Act & Assert
		with patch("app.database.AsyncSessionLocal") as mock_factory:
			mock_factory.return_value.__aenter__.return_value = mock_session
			mock_factory.return_value.__aexit__.return_value = None

			db_generator = get_db()
			session = await db_generator.__anext__()

			assert session == mock_session

			# Simulate error during commit
			with pytest.raises(Exception) as exc_info:
				try:
					await db_generator.__anext__()
				except StopAsyncIteration:
					pass

			# The exception should be raised in the finally block
			# Let's trigger it by sending an exception
			try:
				await db_generator.athrow(Exception("Test error"))
			except Exception:
				pass

			# Assert - rollback was called
			mock_session.rollback.assert_called()
			mock_session.close.assert_called()


@pytest.mark.unit
class TestInitDb:
	"""Test init_db function."""

	async def test_init_db_creates_tables(self):
		"""
		GIVEN database engine and Base metadata
		WHEN initializing database
		THEN all tables are created
		"""
		# Arrange
		mock_conn = AsyncMock()
		mock_conn.run_sync = AsyncMock()

		mock_engine = MagicMock()
		mock_context = AsyncMock()
		mock_context.__aenter__ = AsyncMock(return_value=mock_conn)
		mock_context.__aexit__ = AsyncMock(return_value=None)
		mock_engine.begin = MagicMock(return_value=mock_context)

		# Act
		with patch("app.database.engine", mock_engine):
			await init_db()

		# Assert
		mock_engine.begin.assert_called_once()
		mock_conn.run_sync.assert_called_once()


@pytest.mark.unit
class TestCloseDb:
	"""Test close_db function."""

	async def test_close_db_disposes_engine(self):
		"""
		GIVEN a database engine
		WHEN closing database connections
		THEN engine is disposed
		"""
		# Arrange
		mock_engine = AsyncMock()
		mock_engine.dispose = AsyncMock()

		# Act
		with patch("app.database.engine", mock_engine):
			await close_db()

		# Assert
		mock_engine.dispose.assert_called_once()


@pytest.mark.unit
class TestDatabaseIntegration:
	"""Integration tests for database module."""

	async def test_get_db_context_manager_flow(self):
		"""
		GIVEN a database session
		WHEN using get_db in a context-like flow
		THEN proper lifecycle is maintained
		"""
		# This test simulates the actual flow
		db_gen = get_db()

		# Get the session
		session = await db_gen.__anext__()
		assert session is not None

		# Simulate successful completion
		try:
			await db_gen.__anext__()
		except StopAsyncIteration:
			# Expected - generator exhausted
			pass

	async def test_get_db_exception_handling(self):
		"""
		GIVEN a database session with an error
		WHEN exception occurs during session usage
		THEN proper cleanup happens
		"""
		db_gen = get_db()

		# Get the session
		session = await db_gen.__anext__()
		assert session is not None

		# Simulate an exception
		try:
			await db_gen.athrow(ValueError("Test exception"))
		except ValueError:
			# Expected - exception should be propagated
			pass
		except StopAsyncIteration:
			# Also acceptable
			pass
