"""
Unit tests for UserRepository
Following AAA (Arrange-Act-Assert) pattern
"""

from uuid import uuid4

import pytest

from app.exceptions.user_exceptions import UserAlreadyExistsError
from app.repositories.user_repository import UserRepository
from tests.factories import create_user_data


@pytest.mark.unit
class TestUserRepositoryCreate:
	"""Test UserRepository.create method."""

	async def test_create_user_success(self, test_db_session):
		"""
		GIVEN a valid user data
		WHEN creating a new user
		THEN user is created successfully with all fields
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		user_data = create_user_data(
			name="John Doe", email="john.doe@example.com"
		)

		# Act
		user = await repository.create(user_data)

		# Assert
		assert user is not None
		assert user.name == "John Doe"
		assert user.email == "john.doe@example.com"
		assert user.id is not None
		assert user.created_at is not None
		assert user.updated_at is not None

	async def test_create_user_duplicate_email(self, test_db_session):
		"""
		GIVEN an existing user with an email
		WHEN creating a new user with the same email
		THEN UserAlreadyExistsError is raised
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		user_data = create_user_data(email="duplicate@example.com")
		await repository.create(user_data)

		# Act & Assert
		duplicate_data = create_user_data(email="duplicate@example.com")
		with pytest.raises(UserAlreadyExistsError) as exc_info:
			await repository.create(duplicate_data)

		assert "already exists" in str(exc_info.value)


@pytest.mark.unit
class TestUserRepositoryGetById:
	"""Test UserRepository.get_by_id method."""

	async def test_get_user_by_id_success(self, test_db_session):
		"""
		GIVEN an existing user in database
		WHEN getting user by id
		THEN correct user is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		user_data = create_user_data()
		created_user = await repository.create(user_data)

		# Act
		retrieved_user = await repository.get_by_id(created_user.id)

		# Assert
		assert retrieved_user is not None
		assert retrieved_user.id == created_user.id
		assert retrieved_user.email == created_user.email
		assert retrieved_user.name == created_user.name

	async def test_get_user_by_id_not_found(self, test_db_session):
		"""
		GIVEN a non-existent user id
		WHEN getting user by id
		THEN None is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		non_existent_id = uuid4()

		# Act
		user = await repository.get_by_id(non_existent_id)

		# Assert
		assert user is None


@pytest.mark.unit
class TestUserRepositoryGetAll:
	"""Test UserRepository.get_all method."""

	async def test_get_all_users_empty(self, test_db_session):
		"""
		GIVEN an empty database
		WHEN getting all users
		THEN empty list is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)

		# Act
		users = await repository.get_all()

		# Assert
		assert users == []

	async def test_get_all_users_with_pagination(self, test_db_session):
		"""
		GIVEN multiple users is database
		WHEN getting users with pagination
		THEN correct subset of users is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		for i in range(5):
			user_data = create_user_data(email=f"user{i}@example.com")
			await repository.create(user_data)

		# Act
		users_page_1 = await repository.get_all(skip=0, limit=2)
		users_page_2 = await repository.get_all(skip=2, limit=2)

		# Assert
		assert len(users_page_1) == 2
		assert len(users_page_2) == 2
		assert users_page_1[0].id != users_page_2[0].id


@pytest.mark.unit
class TestUserRepositoryUpdate:
	"""Test UserRepository.update method."""

	async def test_update_user_success(self, test_db_session):
		"""
		GIVEN an existing user
		WHEN updating user data
		THEN user is updated successfully
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		user_data = create_user_data(name="Original Name")
		created_user = await repository.create(user_data)

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="Updated Name")

		# Act
		updated_user = await repository.update(created_user.id, update_data)

		# Assert
		assert updated_user is not None
		assert updated_user.name == "Updated Name"
		assert updated_user.email == created_user.email
		assert updated_user.id == created_user.id

	async def test_update_user_not_found(self, test_db_session):
		"""
		GIVEN a non-existent user id
		WHEN updating user
		THEN None is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		non_existent_id = uuid4()

		from app.models.user import UserUpdate

		update_data = UserUpdate(name="New Name")

		# Act
		result = await repository.update(non_existent_id, update_data)

		# Assert
		assert result in None


@pytest.mark.unit
class TestUserRepositoryDelete:
	"""Test UserRepository.delete method."""

	async def test_delete_user_success(self, test_db_session):
		"""
		GIVEN an existing user
		WHEN deleting the user
		THEN user is deleted and True is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		user_data = create_user_data()
		created_user = await repository.create(user_data)

		# Act
		result = await repository.delete(created_user.id)

		# Assert
		assert result is True
		deleted_user = await repository.get_by_id(created_user.id)
		assert deleted_user is None

	async def test_delete_user_not_found(self, test_db_session):
		"""
		GIVEN a non-existent user id
		WHEN deleting user
		THEN False is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		non_existent_id = uuid4()

		# Act
		result = await repository.delete(non_existent_id)

		# Assert
		assert result is False


@pytest.mark.unit
class TestUserRepositoryCount:
	"""Test UserRepository.count method."""

	async def test_count_users_empty(self, test_db_session):
		"""
		GIVEN an empty database
		WHEN counting users
		THEN 0 is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)

		# Act
		count = await repository.count()

		# Assert
		assert count == 0

	async def test_count_users_multiple(self, test_db_session):
		"""
		GIVEN multiple users in database
		WHEN counting users
		THEN correct count is returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		for i in range(3):
			user_data = create_user_data(email=f"user{i}@example.com")
			await repository.create(user_data)

		# Act
		count = await repository.count()

		# Assert
		assert count == 3
