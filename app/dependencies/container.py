"""
Dependency injection container demonstrating
Dependency Inversion Principle (DIP)
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


class Container:
	"""
	Dependency injection container following DIP principle

	DIP: High-level modules depend on abstractions, not concretions
	This container manages the creation and injection of dependencies
	"""

	def user_repository(self, session: AsyncSession) -> UserRepository:
		"""
		Get user repository instance

		Args:
			session: Database session

		Returns:
			UserRepository instance
		"""
		logger.info("Creating UserRepository instance with database session")
		return UserRepository(session)

	def user_service(self, session: AsyncSession) -> UserService:
		"""
		Get user service instance

		Args:
			session: Database session

		Returns:
			UserService instance with injected dependencies
		"""
		# Dependency injection: UserService depends on
		# UserRepository abstraction
		user_repository = self.user_repository(session)
		logger.info("Creating UserService instance with injected dependencies")
		return UserService(user_repository)
