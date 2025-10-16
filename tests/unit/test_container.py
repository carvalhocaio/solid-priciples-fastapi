"""
Unit tests for dependency injection container
Following AAA (Arrange-Act-Assert) pattern
"""
import pytest

from app.dependencies.container import Container
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.mark.unit
class TestContainer:
	"""Test Container dependency injection."""

	async def test_container_creates_repository(self, test_db_session):
		"""
		GIVEN a container and database session
		WHEN getting user repository
		THEN UserRepository instance is returned
		"""
		# Arrange
		container = Container()

		# Act
		repository = container.user_repository(test_db_session)

		# Assert
		assert isinstance(repository, UserRepository)
		assert repository.session == test_db_session

	async def test_container_creates_service(self, test_db_session):
		"""
		GIVEN a container and database session
		WHEN getting user service
		THEN UserService instance is returned with injected repository
		"""
		# Arrange
		container = Container()

		# Act
		service = container.user_service(test_db_session)

		# Assert
		assert isinstance(service, UserService)
		assert isinstance(service._user_repository, UserRepository)

	async def test_container_repository_uses_correct_session(
		self, test_db_session
	):
		"""
		GIVEN a container with specific session
		WHEN creating repository
		THEN repository uses the provided session
		"""
		# Arrange
		container = Container()

		# Act
		repository = container.user_repository(test_db_session)

		# Assert
		assert repository.session is test_db_session

	async def test_container_creates_new_instances(self, test_db_session):
		"""
		GIVEN a container
		WHEN calling factory methods multiple times
		THEN new instances are created each time
		"""
		# Arrange
		container = Container()

		# Act
		service1 = container.user_service(test_db_session)
		service2 = container.user_service(test_db_session)

		# Assert
		assert service1 is not service2
		assert service1._user_repository is not service2._user_repository
