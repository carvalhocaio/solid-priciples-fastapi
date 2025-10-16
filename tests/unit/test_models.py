"""
Unit tests for Pydantic models
Following AAA (Arrange-Act-Assert) pattern
"""

from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.user import User, UserCreate, UserResponse, UserUpdate


@pytest.mark.unit
class TestUserCreateModel:
	"""Test UserCreate model validation."""

	def test_create_user_valid(self):
		"""
		GIVEN valid user data
		WHEN creating UserCreate instance
		THEN model is created successfully
		"""
		# Arrange
		data = {"name": "John Doe", "email": "john.doe@example.com"}

		# Act
		user_create = UserCreate(**data)

		# Assert
		assert user_create.name == "John Doe"
		assert user_create.email == "john.doe@example.com"

	def test_create_user_invalid_email(self):
		"""
		GIVEN invalid email format
		WHEN creating UserCreate instance
		THEN ValidationError is raised
		"""
		# Arrange
		data = {"name": "John Doe", "email": "invalid-email"}

		# Act & Assert
		with pytest.raises(ValidationError) as exc_info:
			UserCreate(**data)

		assert "email" in str(exc_info.value)

	def test_create_user_missing_name(self):
		"""
		GIVEN missing name field
		WHEN creating UserCreate instance
		THEN ValidationError is raised
		"""
		# Arrange
		data = {"email": "john.doe@example.com"}

		# Act & Assert
		with pytest.raises(ValidationError) as exc_info:
			UserCreate(**data)

		assert "name" in str(exc_info.value)

	def test_create_user_missing_email(self):
		"""
		GIVEN missing email field
		WHEN creating UserCreate instance
		THEN ValidationError is raised
		"""
		# Arrange
		data = {"name": "John Doe"}

		# Act & Assert
		with pytest.raises(ValidationError) as exc_info:
			UserCreate(**data)

		assert "email" in str(exc_info.value)

	def test_create_user_empty_name(self):
		"""
		GIVEN empty name string
		WHEN creating UserCreate instance
		THEN ValidationError is raised
		"""
		# Arrange
		data = {"name": "", "email": "john.doe@example.com"}

		# Act & Assert
		with pytest.raises(ValidationError) as exc_info:
			UserCreate(**data)

		assert "name" in str(exc_info.value)

	def test_create_user_name_too_long(self):
		"""
		GIVEN name exceeding max length
		WHEN creating UserCreate instance
		THEN ValidationError is raised
		"""
		# Arrange
		data = {
			"name": "a" * 101,  # max is 100
			"email": "john.doe@example.com",
		}

		# Act & Assert
		with pytest.raises(ValidationError) as exc_info:
			UserCreate(**data)

		assert "name" in str(exc_info.value)


@pytest.mark.unit
class TestUserUpdateModel:
	"""Test UserUpdate model validation."""

	def test_update_user_all_fields(self):
		"""
		GIVEN all fields for update
		WHEN creating UserUpdate instance
		THEN model is created successfully
		"""
		# Arrange
		data = {"name": "Updated Name", "email": "updated@example.com"}

		# Act
		user_update = UserUpdate(**data)

		# Assert
		assert user_update.name == "Updated Name"
		assert user_update.email == "updated@example.com"

	def test_update_user_partial_name_only(self):
		"""
		GIVEN only name field
		WHEN creating UserUpdate instance
		THEN model is created with name, email is None
		"""
		# Arrange
		data = {"name": "Updated Name"}

		# Act
		user_update = UserUpdate(**data)

		# Assert
		assert user_update.name == "Updated Name"
		assert user_update.email is None

	def test_update_user_partial_email_only(self):
		"""
		GIVEN only email field
		WHEN creating UserUpdate instance
		THEN model is created with email, name is None
		"""
		# Arrange
		data = {"email": "updated@example.com"}

		# Act
		user_update = UserUpdate(**data)

		# Assert
		assert user_update.name is None
		assert user_update.email == "updated@example.com"

	def test_update_user_empty_body(self):
		"""
		GIVEN empty update data
		WHEN creating UserUpdate instance
		THEN model is created with all None values
		"""
		# Arrange
		data = {}

		# Act
		user_update = UserUpdate(**data)

		# Assert
		assert user_update.name is None
		assert user_update.email is None

	def test_update_user_invalid_email(self):
		"""
		GIVEN invalid email format
		WHEN creating UserUpdate instance
		THEN ValidationError is raised
		"""
		# Arrange
		data = {"email": "invalid-email"}

		# Act & Assert
		with pytest.raises(ValidationError) as exc_info:
			UserUpdate(**data)

		assert "email" in str(exc_info.value)


@pytest.mark.unit
class TestUserModel:
	"""Test User model."""

	def test_user_model_creation(self):
		"""
		GIVEN valid user data
		WHEN creating User instance
		THEN model is created with all fields
		"""
		# Arrange
		data = {"name": "John Doe", "email": "john.doe@example.com"}

		# Act
		user = User(**data)

		# Assert
		assert user.name == "John Doe"
		assert user.email == "john.doe@example.com"
		assert isinstance(user.id, UUID)
		assert isinstance(user.created_at, datetime)
		assert isinstance(user.updated_at, datetime)

	def test_user_model_with_custom_id(self):
		"""
		GIVEN user data with custom UUID
		WHEN creating User instance
		THEN custom UUID is used
		"""
		# Arrange
		from uuid import uuid4

		custom_id = uuid4()
		data = {
			"id": custom_id,
			"name": "John Doe",
			"email": "john.doe@example.com",
		}

		# Act
		user = User(**data)

		# Assert
		assert user.id == custom_id


@pytest.mark.unit
class TestUserResponseModel:
	"""Test UserResponse model."""

	def test_user_response_from_user(self):
		"""
		GIVEN a User instance
		WHEN creating UserResponse
		THEN response model is created correctly
		"""
		# Arrange
		user = User(name="John Doe", email="john.doe@example.com")

		# Act
		response = UserResponse.model_validate(user)

		# Assert
		assert response.name == user.name
		assert response.email == user.email
		assert response.id == user.id
		assert response.created_at == user.created_at
		assert response.updated_at == user.updated_at

	def test_user_response_serialization(self):
		"""
		GIVEN a UserResponse instance
		WHEN converting to dict
		THEN all fields are serialized correctly
		"""
		# Arrange
		user = User(name="John Doe", email="john.doe@example.com")
		response = UserResponse.model_validate(user)

		# Act
		data = response.model_dump()

		# Assert
		assert "id" in data
		assert "name" in data
		assert "email" in data
		assert "created_at" in data
		assert "updated_at" in data
		assert data["name"] == "John Doe"
