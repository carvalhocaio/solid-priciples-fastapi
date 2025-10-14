"""
User repository implementation demonstrating Liskov Substitution Principle (LSP)
and Dependency Inversion Principle (DIP)
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.user_exceptions import (
	UserAlreadyExistsError,
)
from app.models.db_models import UserDB
from app.models.user import User, UserCreate, UserUpdate
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
	"""
	SQLAlchemy user repository implementation

	LSP: Can be substituted for BaseRepository without breaking functionality
	DIP: Depends on abstraction (BaseRepository) not concrete implementation
	SRP: Only responsible for user data persistence
	"""

	def __init__(self, session: AsyncSession):
		"""
		Initialize repository with database session

		Args:
			session: SQLAlchemy async session
		"""
		self.session = session
		logger.info("UserRepository initialized with SQLAlchemy session")

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
			raise UserAlreadyExistsError(
				f"User with email {user_data.email} already exists"
			)

		# Create database model
		db_user = UserDB(
			name=user_data.name,
			email=user_data.email,
		)

		self.session.add(db_user)
		await self.session.flush()
		await self.session.refresh(db_user)

		logger.info(f"User created with ID: {db_user.id}")

		# Convert to Pydantic model
		return self._to_pydantic(db_user)

	async def get_by_id(self, user_id: UUID) -> Optional[User]:
		"""
		Get user by ID

		Args:
			user_id: User ID

		Returns:
			User if found, None otherwise
		"""
		stmt = select(UserDB).where(UserDB.id == str(user_id))
		result = await self.session.execute(stmt)
		db_user = result.scalar_one_or_none()

		if db_user:
			logger.info(f"User found with ID: {user_id}")
			return self._to_pydantic(db_user)
		else:
			logger.warning(f"User not found with ID: {user_id}")
			return None

	async def get_all(self, skip: int = 0, limit: int = 10) -> List[User]:
		"""
		Get all users with pagination

		Args:
			skip: Number of users to skip
			limit: Maximum number of users to return

		Returns:
			List of users
		"""
		stmt = select(UserDB).offset(skip).limit(limit)
		result = await self.session.execute(stmt)
		db_users = result.scalars().all()

		logger.info(
			f"Retrieved {len(db_users)} users (skip: {skip}, limit: {limit})"
		)

		return [self._to_pydantic(db_user) for db_user in db_users]

	async def update(
		self, user_id: UUID, user_data: UserUpdate
	) -> Optional[User]:
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
		stmt = select(UserDB).where(UserDB.id == str(user_id))
		result = await self.session.execute(stmt)
		db_user = result.scalar_one_or_none()

		if not db_user:
			logger.warning(f"User not found for update with ID: {user_id}")
			return None

		updated_data = user_data.model_dump(exclude_unset=True)

		# Check email uniqueness if email is being updated
		if "email" in updated_data and updated_data["email"] != db_user.email:
			existing_user = await self._get_by_email(updated_data["email"])
			if existing_user and existing_user.id != user_id:
				raise UserAlreadyExistsError(
					f"User with email {updated_data['email']} already exists"
				)

		# Update fields
		for field, value in updated_data.items():
			setattr(db_user, field, value)

		db_user.updated_at = datetime.utcnow()
		await self.session.flush()
		await self.session.refresh(db_user)

		logger.info(f"User updated with ID: {user_id}")
		return self._to_pydantic(db_user)

	async def delete(self, user_id: UUID) -> bool:
		"""
		Delete user

		Args:
			user_id: User ID

		Returns:
			True if user was deleted, False if not found
		"""
		stmt = select(UserDB).where(UserDB.id == str(user_id))
		result = await self.session.execute(stmt)
		db_user = result.scalar_one_or_none()

		if db_user:
			await self.session.delete(db_user)
			await self.session.flush()
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
		stmt = select(func.count()).select_from(UserDB)
		result = await self.session.execute(stmt)
		count = result.scalar_one()

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
		stmt = select(UserDB).where(UserDB.email == email)
		result = await self.session.execute(stmt)
		db_user = result.scalar_one_or_none()

		if db_user:
			return self._to_pydantic(db_user)
		return None

	def _to_pydantic(self, db_user: UserDB) -> User:
		"""
		Convert SQLAlchemy model to Pydantic model

		Args:
			db_user: SQLAlchemy UserDB instance

		Returns:
			Pydantic User instance
		"""
		return User(
			id=UUID(db_user.id),
			name=db_user.name,
			email=db_user.email,
			created_at=db_user.created_at,
			updated_at=db_user.updated_at,
		)
