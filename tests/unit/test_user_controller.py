"""
Unit tests for UserController
Testing controller logic with mocked dependencies
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.controllers.user_controller import UserController
from app.dependencies.container import Container
from app.exceptions.user_exceptions import (
	UserAlreadyExistsError,
	UserNotFoundError,
)
from tests.factories import create_user, create_user_data


@pytest.mark.unit
class TestUserControllerCreate:
	"""Test UserController.create_user method."""

	async def test_create_user_success(self):
		"""
		GIVEN valid user data
		WHEN creating a user through controller
		THEN user is created successfully
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		expected_user = create_user(name="Test User")
		mock_service.create.return_value = expected_user
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)
		user_data = create_user_data(name="Test User")

		# Act
		result = await controller.create_user(user_data, mock_session)

		# Assert
		assert result.name == "Test User"
		mock_service.create.assert_called_once_with(user_data)

	async def test_create_user_already_exists(self):
		"""
		GIVEN a duplicate email
		WHEN creating a user
		THEN 409 Conflict is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		mock_service.create.side_effect = UserAlreadyExistsError(
			"Email already exists"
		)
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)
		user_data = create_user_data()

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.create_user(user_data, mock_session)

		assert exc_info.value.status_code == 409

	async def test_create_user_internal_error(self):
		"""
		GIVEN an unexpected error during creation
		WHEN creating a user
		THEN 500 Internal Server Error is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		mock_service.create.side_effect = Exception("Unexpected error")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)
		user_data = create_user_data()

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.create_user(user_data, mock_session)

		assert exc_info.value.status_code == 500
		assert "Internal server error" in str(exc_info.value.detail)


@pytest.mark.unit
class TestUserControllerGet:
	"""Test UserController.get_user method."""

	async def test_get_user_success(self):
		"""
		GIVEN an existing user id
		WHEN getting user
		THEN user is returned
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		expected_user = create_user(id=user_id)
		mock_service.get_by_id.return_value = expected_user
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act
		result = await controller.get_user(user_id, mock_session)

		# Assert
		assert result.id == user_id
		mock_service.get_by_id.assert_called_once_with(user_id)

	async def test_get_user_not_found(self):
		"""
		GIVEN a non-existent user id
		WHEN getting user
		THEN 404 Not Found is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.get_by_id.side_effect = UserNotFoundError(
			"User not found"
		)
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.get_user(user_id, mock_session)

		assert exc_info.value.status_code == 404

	async def test_get_user_internal_error(self):
		"""
		GIVEN an unexpected error during retrieval
		WHEN getting user
		THEN 500 Internal Server Error is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.get_by_id.side_effect = Exception("Unexpected error")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.get_user(user_id, mock_session)

		assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestUserControllerGetAll:
	"""Test UserController.get_users method."""

	async def test_get_all_users_success(self):
		"""
		GIVEN users in database
		WHEN getting all users
		THEN paginated list is returned
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		users = [create_user() for _ in range(3)]
		mock_service.get_all.return_value = (users, 3)
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act
		result = await controller.get_users(
			page=1, per_page=10, session=mock_session
		)

		# Assert
		assert len(result.users) == 3
		assert result.total == 3
		assert result.page == 1
		assert result.per_page == 10
		mock_service.get_all.assert_called_once_with(0, 10)

	async def test_get_all_users_internal_error(self):
		"""
		GIVEN an unexpected error during retrieval
		WHEN getting all users
		THEN 500 Internal Server Error is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		mock_service.get_all.side_effect = Exception("Unexpected error")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.get_users(session=mock_session)

		assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestUserControllerUpdate:
	"""Test UserController.update_user method."""

	async def test_update_user_success(self):
		"""
		GIVEN an existing user and update data
		WHEN updating user
		THEN user is updated successfully
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		updated_user = create_user(id=user_id, name="Updated Name")
		mock_service.update.return_value = updated_user
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="Updated Name")

		# Act
		result = await controller.update_user(
			user_id, update_data, mock_session
		)

		# Assert
		assert result.name == "Updated Name"
		mock_service.update.assert_called_once_with(user_id, update_data)

	async def test_update_user_not_found(self):
		"""
		GIVEN a non-existent user id
		WHEN updating user
		THEN 404 Not Found is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.update.side_effect = UserNotFoundError("User not found")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="Updated Name")

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.update_user(user_id, update_data, mock_session)

		assert exc_info.value.status_code == 404

	async def test_update_user_duplicate_email(self):
		"""
		GIVEN a duplicate email during update
		WHEN updating user
		THEN 409 Conflict is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.update.side_effect = UserAlreadyExistsError(
			"Email already exists"
		)
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		from app.models.user import UserUpdate

		update_data = UserUpdate(email="duplicate@test.com")

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.update_user(user_id, update_data, mock_session)

		assert exc_info.value.status_code == 409

	async def test_update_user_internal_error(self):
		"""
		GIVEN an unexpected error during update
		WHEN updating user
		THEN 500 Internal Server Error is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.update.side_effect = Exception("Unexpected error")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="New Name")

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.update_user(user_id, update_data, mock_session)

		assert exc_info.value.status_code == 500


@pytest.mark.unit
class TestUserControllerDelete:
	"""Test UserController.delete_user method."""

	async def test_delete_user_success(self):
		"""
		GIVEN an existing user id
		WHEN deleting user
		THEN 204 No Content is returned
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.delete.return_value = True
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act
		result = await controller.delete_user(user_id, mock_session)

		# Assert
		assert result.status_code == 204
		mock_service.delete.assert_called_once_with(user_id)

	async def test_delete_user_not_found(self):
		"""
		GIVEN a non-existent user id
		WHEN deleting user
		THEN 404 Not Found is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.delete.side_effect = UserNotFoundError("User not found")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.delete_user(user_id, mock_session)

		assert exc_info.value.status_code == 404

	async def test_delete_user_internal_error(self):
		"""
		GIVEN an unexpected error during deletion
		WHEN deleting user
		THEN 500 Internal Server Error is raised
		"""
		# Arrange
		mock_container = MagicMock(spec=Container)
		mock_service = AsyncMock()
		mock_session = MagicMock()

		user_id = uuid4()
		mock_service.delete.side_effect = Exception("Unexpected error")
		mock_container.user_service.return_value = mock_service

		controller = UserController(mock_container)

		# Act & Assert
		with pytest.raises(HTTPException) as exc_info:
			await controller.delete_user(user_id, mock_session)

		assert exc_info.value.status_code == 500
