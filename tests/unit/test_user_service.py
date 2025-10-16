"""
Unit tests for UserService using mocks
Following AAA (Arrange-Act-Assert) pattern
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.exceptions.user_exceptions import UserNotFoundError
from app.services.user_service import UserService
from tests.factories import create_user, create_user_data


@pytest.mark.unit
class TestUserServiceCreate:
	"""Test UserService.create method."""

	async def test_create_user_success(self):
		"""
		GIVEN valid user data and a mocked repository
		WHEN creating a new user
		THEN repository.create is called and user is returned
		"""
		# Arrange
		mock_repository = AsyncMock()
		expected_user = create_user(name="John Doe")
		mock_repository.create.return_value = expected_user

		service = UserService(mock_repository)
		user_data = create_user_data(name="John Doe")

		# Act
		result = await service.create(user_data)

		# Assert
		mock_repository.create.assert_called_once_with(user_data)
		assert result == expected_user
		assert result.name == "John Doe"


@pytest.mark.unit
class TestUserServiceGetById:
	"""Test UserService.get_by_id method."""

	async def test_get_user_by_id_success(self):
		"""
		GIVEN an existing user id and mocked repository
		WHEN getting user by id
		THEN repository.get_by_id is called and user is returned
		"""
		# Arrange
		mock_repository = AsyncMock()
		user_id = uuid4()
		excepted_user = create_user(id=user_id)
		mock_repository.get_by_id.return_value = excepted_user

		service = UserService(mock_repository)

		# Act
		result = await service.get_by_id(user_id)

		# Assert
		mock_repository.get_by_id.assert_called_once_with(user_id)
		assert result == excepted_user
		assert result.id == user_id

	async def test_get_user_by_id_not_found(self):
		"""
		GIVEN a non-existent user id
		WHEN getting user by id
		THEN UserNotFoundError is raised
		"""
		# Arrange
		mock_repository = AsyncMock()
		user_id = uuid4()
		mock_repository.get_by_id.return_value = None

		service = UserService(mock_repository)

		# Act & Assert
		with pytest.raises(UserNotFoundError) as exc_info:
			await service.get_by_id(user_id)

		assert str(user_id) in str(exc_info.value)
		mock_repository.get_by_id.assert_called_once_with(user_id)


@pytest.mark.unit
class TestUserServiceGetAll:
	"""Test UserService.get_all method."""

	async def test_get_all_users_success(self):
		"""
		GIVEN multiple users and mocked repository
		WHEN getting all users
		THEN repository methods are called and users with count are returned
		"""
		# Arrange
		mock_repository = AsyncMock()
		expected_users = [create_user() for _ in range(3)]
		mock_repository.get_all.return_value = expected_users
		mock_repository.count.return_value = 3

		service = UserService(mock_repository)

		# Act
		users, count = await service.get_all(skip=0, limit=10)

		# Assert
		mock_repository.get_all.assert_called_once_with(0, 10)
		mock_repository.count.assert_called_once()
		assert users == expected_users
		assert count == 3
		assert len(users) == 3

	async def test_get_all_users_with_pagination_validation(self):
		"""
		GIVEN invalid pagination parameters
		WHEN getting all users
		THEN parameters are validated and corrected
		"""
		# Arrange
		mock_repository = AsyncMock()
		mock_repository.get_all.return_value = []
		mock_repository.count.return_value = 0

		service = UserService(mock_repository)

		# Act - negative skip
		await service.get_all(skip=-5, limit=10)

		# Assert - skip should be corrected to 0
		mock_repository.get_all.assert_called_with(0, 10)

		# Act - invalid limit (too large)
		await service.get_all(skip=0, limit=200)

		# Assert - limit should be corrected to 10 (default)
		mock_repository.get_all.assert_called_with(0, 10)


@pytest.mark.unit
class TestUserServiceUpdate:
	"""Test UserService.update method."""

	async def test_update_user_success(self):
		"""
		GIVEN an existing user and update data
		WHEN updating the user
		THEN user is updated successfully
		"""
		# Arrange
		mock_repository = AsyncMock()
		user_id = uuid4()
		existing_user = create_user(id=user_id, name="Old Name")
		updated_user = create_user(id=user_id, name="New Name")

		mock_repository.get_by_id.return_value = existing_user
		mock_repository.update.return_value = updated_user

		service = UserService(mock_repository)

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="New Name")

		# Act
		result = await service.update(user_id, update_data)

		# Assert
		mock_repository.get_by_id.assert_called_once_with(user_id)
		mock_repository.update.assert_called_once_with(user_id, update_data)
		assert result.name == "New Name"

	async def test_update_user_not_found_on_get(self):
		"""
		GIVEN a non-existent user id
		WHEN updating user
		THEN UserNotFoundError is raised before update attempt
		"""
		# Arrange
		mock_repository = AsyncMock()
		user_id = uuid4()
		mock_repository.get_by_id.return_value = None

		service = UserService(mock_repository)

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="New Name")

		# Act & Assert
		with pytest.raises(UserNotFoundError):
			await service.update(user_id, update_data)

		# Update should not be called if user doesn't exist
		mock_repository.update.assert_not_called()


@pytest.mark.unit
class TestUserServiceDelete:
	"""Test UserService.delete method."""

	async def test_delete_user_success(self):
		"""
		GIVEN an existing user
		WHEN deleting the user
		THEN user is deleted successfully
		"""
		# Arrange
		mock_repository = AsyncMock()
		user_id = uuid4()
		existing_user = create_user(id=user_id)

		mock_repository.get_by_id.return_value = existing_user
		mock_repository.delete.return_value = True

		service = UserService(mock_repository)

		# Act
		result = await service.delete(user_id)

		# Assert
		mock_repository.get_by_id.assert_called_once_with(user_id)
		mock_repository.delete.assert_called_once_with(user_id)
		assert result is True

	async def test_delete_user_not_found(self):
		"""
		GIVEN a non-existent user id
		WHEN deleting user
		THEN UserNotFoundError is raised
		"""
		# Arrange
		mock_repository = AsyncMock()
		user_id = uuid4()
		mock_repository.get_by_id.return_value = None

		service = UserService(mock_repository)

		# Act & Assert
		with pytest.raises(UserNotFoundError):
			await service.delete(user_id)

		# Delete should not be called if user doesn't exist
		mock_repository.delete.assert_not_called()
