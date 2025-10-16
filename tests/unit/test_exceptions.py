"""
Unit tests for custom exceptions
Following AAA (Arrange-Act-Assert) pattern
"""

import pytest

from app.exceptions.user_exceptions import (
	UserAlreadyExistsError,
	UserNotFoundError,
)


@pytest.mark.unit
class TestUserNotFoundError:
	"""Test UserNotFoundError exception."""

	def test_exception_default_message(self):
		"""
		GIVEN no custom message
		WHEN raising UserNotFoundError
		THEN default message is used
		"""
		# Arrange & Act
		exception = UserNotFoundError()

		# Assert
		assert str(exception) == "User not found"
		assert exception.message == "User not found"

	def test_exception_custom_message(self):
		"""
		GIVEN custom error message
		WHEN raising UserNotFoundError
		THEN custom message is used
		"""
		# Arrange
		custom_message = "User with ID 123 not found"

		# Act
		exception = UserNotFoundError(custom_message)

		# Assert
		assert str(exception) == custom_message
		assert exception.message == custom_message

	def test_exception_can_be_raised(self):
		"""
		GIVEN UserNotFoundError
		WHEN raising exception
		THEN exception can be caught
		"""
		# Arrange & Act & Assert
		with pytest.raises(UserNotFoundError) as exc_info:
			raise UserNotFoundError("Test error")

		assert "Test error" in str(exc_info.value)

	def test_exception_inheritance(self):
		"""
		GIVEN UserNotFoundError
		WHEN checking inheritance
		THEN it inherits from Exception
		"""
		# Arrange
		exception = UserNotFoundError()

		# Act & Assert
		assert isinstance(exception, Exception)


@pytest.mark.unit
class TestUserAlreadyExistsError:
	"""Test UserAlreadyExistsError exception."""

	def test_exception_default_message(self):
		"""
		GIVEN no custom message
		WHEN raising UserAlreadyExistsError
		THEN default message is used
		"""
		# Arrange & Act
		exception = UserAlreadyExistsError()

		# Assert
		assert str(exception) == "User already exists"
		assert exception.message == "User already exists"

	def test_exception_custom_message(self):
		"""
		GIVEN custom error message
		WHEN raising UserAlreadyExistsError
		THEN custom message is used
		"""
		# Arrange
		custom_message = "User with email test@example.com already exists"

		# Act
		exception = UserAlreadyExistsError(custom_message)

		# Assert
		assert str(exception) == custom_message
		assert exception.message == custom_message

	def test_exception_can_be_raised(self):
		"""
		GIVEN UserAlreadyExistsError
		WHEN raising exception
		THEN exception can be caught
		"""
		# Arrange & Act & Assert
		with pytest.raises(UserAlreadyExistsError) as exc_info:
			raise UserAlreadyExistsError("Test error")

		assert "Test error" in str(exc_info.value)

	def test_exception_inheritance(self):
		"""
		GIVEN UserAlreadyExistsError
		WHEN checking inheritance
		THEN it inherits from Exception
		"""
		# Arrange
		exception = UserAlreadyExistsError()

		# Act & Assert
		assert isinstance(exception, Exception)
