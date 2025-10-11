"""
User repository implementation demonstrating Liskov Substitution Principle (LSP)
and Dependency Inversion Principle (DIP)
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from app.models.user import User, UserCreate, UserUpdate
from app.repositories.base import BaseRepository
from app.exceptions.user_exceptions import UserNotFoundError, UserAlreadyExistsError

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
	"""
	In-memory user repository implementation

	LSP: Can be substituted for BaseRepository without breaking functionality
	DIP: Depends on abstraction (BaseRepository) not concrete implementation
	SRP: Only responsible for user data persistence
	"""

	def __init__(self):
		# In-memory storage (can be easily replaced with database implementation)
		self._users: Dict[UUID, User] = {}
		logger.info("UserRepository initialized with in-memory storage")

	async def create(self, user_data: UserCreate) -> User:
		"""
		Create a new user

		Args:
			user_data: User creation data

		Returns:
			Created user

		Raises:
			UserAlreadyExistsError: If user with email already exits
		"""
		# Check if user with email already exists
		existing_user = await self._get_by_email(user_data.email)
		if existing_user:
			raise UserAlreadyExistsError(f"User with email {user_data.email} already exists")

		user = User(
			name=user_data.name,
			email=user_data.email,
		)

		self._users[user.id] = user
		logger.info(f"User created with ID: {user.id}")
		return user

	async def get_by_id(self, user_id: UUID) -> Optional[User]:
		"""
		Get user by ID

		Args:
			user_id: User ID

		Returns:
			User if found, None otherwise
		"""
		user = self._users.get(user_id)
		if user:
			logger.info(f"User found with ID: {user_id}")
		else:
			logger.warning(f"User not found with ID: {user_id}")
		return user

	async def get_all(self, skip: int = 0, limit: int = 10) -> List[User]:
		"""
		Get all users with pagination

		Args:
			skip: Number of users to skip
			limit: Maximum number of users to return

		Returns:
			List of users
		"""
		users = list(self._users.values())
		paginated_users = users[skip:skip + limit]
		logger.info(f"Retrieved {len(paginated_users)} users (skip: {skip}, limit: {limit})")
		return paginated_users

	async def update(self, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
		"""
		Update user

		Args:
			user_id: User ID
			user_data: User update data

		Returns:
			Updated user if found, None otherwise

		Raises:
			UserAlreadyExistsError: If email is being changed to an existing email
		"""
		user = self._users.get(user_id)
		if not user:
			logger.warning(f"User not found for update with ID: {user_id}")
			return None

		updated_data = user_data.model_dump(exclude_unset=True)

		# Check email uniqueness if email is being updated
		if "email" in updated_data and updated_data["email"] != user.email:
			existing_user = await self._get_by_email(updated_data["email"])
			if existing_user and existing_user.id != user_id:
				raise UserAlreadyExistsError(f"User with email {updated_data['email']} already exists")

		# Update fields
		for field, value in updated_data.items():
			setattr(user, field, value)

		user.updated_at = datetime.utcnow()
		logger.info(f"User updated with ID: {user_id}")
		return user

	async def delete(self, user_id: UUID) -> bool:
		"""
		Delete user

		Args:
			user_id: User ID

		Returns:
			True if user was deleted, False if not found
		"""
		if user_id in self._users:
			del self._users[user_id]
			logger.info(f"User deleted with ID: {user_id}")
			return True

		logger.warning(f"User not found for deletion with ID: {user_id}")
		return False

	async def count(self) -> int:
		"""
		Get total count of users

		Returns:
			Total number of users
		"""
		count = len(self._users)
		logger.info(f"Total users count: {count}")
		return count

	async def _get_by_email(self, email: str) -> Optional[User]:
		"""
		Helper method to get user by email

		Args:
			email: User email

		Returns:
			User if found, None otherwise
		"""
		for user in self._users.values():
			if user.email == email:
				return user
		return None
