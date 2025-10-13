"""
User service implementation demonstrating business logic layer
and following SOLID principles
"""

import logging
from typing import List, Tuple
from uuid import UUID

from app.exceptions.user_exceptions import UserNotFoundError
from app.models.user import User, UserCreate, UserUpdate
from app.repositories.base import BaseRepository
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService[User, UserCreate, UserUpdate]):
	"""
	User service implementing business logic

	SRP: Only responsible for user business logic
	DIP: Depends on abstraction (BaseRepository) not concrete implementation
	LSP: Can be substituted for BaseService without breaking functionality
	"""

	def __init__(self, user_repository: BaseRepository[User]):
		"""
		Initialize user service with dependency injection

		Args:
			user_repository: User repository implementation
		"""
		self._user_repository = user_repository
		logger.info("UserService initialized")

	async def create(self, user_data: UserCreate) -> User:
		"""
		Create a new user with business logic validation

		Args:
			user_data: User creation data

		Returns:
			Created user
		"""
		logger.info(f"Creating user with email: {user_data.email}")

		# Business logic: Additional validation could be added here
		# For example: checking if name contains prohibited words, etc.

		user = await self._user_repository.create(user_data)
		logger.info(f"User created successfully: {user.id}")
		return user

	async def get_by_id(self, user_id: UUID) -> User:
		"""
		Get user by ID with business logic

		Args:
			user_id: User ID

		Returns:
			User

		Raises:
			UserNotFoundError: If user is not found
		"""
		logger.info(f"Retrieving user with ID: {user_id}")

		user = await self._user_repository.get_by_id(user_id)
		if not user:
			raise UserNotFoundError(f"User with ID {user_id} not found")

		logger.info(f"User retrieved successfully: {user_id}")
		return user

	async def get_all(
		self, skip: int = 0, limit: int = 10
	) -> Tuple[List[User], int]:
		"""
		Get all users with pagination and business logic

		Args:
			skip: Number of users to skip
			limit: Maximum number of users to return

		Returns:
			Tuple of (users list, total count)
		"""
		logger.info(
			f"Retrieving users with pagination (skip: {skip}, limit: {limit})"
		)

		# Business logic: Validate pagination parameters
		skip = max(skip, 0)
		if limit <= 0 or limit > 100:  # Max limit of 100
			limit = 10

		users = await self._user_repository.get_all(skip, limit)
		total_count = await self._user_repository.count()

		logger.info(
			f"Retrieving {len(users)} users out of {total_count} total"
		)
		return users, total_count

	async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
		"""
		Update user with business logic validation

		Args:
			user_id: User ID
			user_data: User update data

		Returns:
			Updated user

		Raises:
			UserNotFoundError: If user is not found
		"""
		logger.info(f"Updating user with ID: {user_id}")

		# Business logic: Ensure user exists first
		await self.get_by_id(
			user_id
		)  # This will raise UserNotFoundError if not found

		# Additional business logic validation could be added here

		updated_user = await self._user_repository.update(user_id, user_data)
		if not updated_user:
			raise UserNotFoundError(f"User with ID {user_id} not found")

		logger.info(f"User updated successfully: {user_id}")
		return updated_user

	async def delete(self, user_id: UUID) -> bool:
		"""
		Delete user with business logic

		Args:
			user_id: User ID

		Returns:
			True if user was deleted

		Raises:
			UserNotFoundError: If user is not found
		"""
		logger.info(f"Deleting user with ID: {user_id}")

		# Business logic: Ensure user exists first
		await self.get_by_id(
			user_id
		)  # This will raise UserNotFoundError if not found

		# Additional business logic could be added here
		# For example: checking if user has related data that needs cleanup

		deleted = await self._user_repository.delete(user_id)
		if not deleted:
			raise UserNotFoundError(f"User with ID {user_id} not found")

		logger.info(f"User deleted successfully: {user_id}")
		return True
