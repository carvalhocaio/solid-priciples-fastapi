"""
Dependency injection container demonstrating Dependency Inversion Principle (DIP)
"""
import logging
from functools import lru_cache

from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


class Container:
	"""
	Dependency injection container following DIP principle

	DIP: High-level modules depend on abstractions, not concretions
	This container manages the creation and injection of dependencies
	"""

	def __init__(self):
		"""Initialize the container"""
		self._user_repository = None
		self._user_service = None
		logger.info("Dependency container initialized")

	@lru_cache(maxsize=1)
	def user_repository(self) -> UserRepository:
		"""
		Get user repository instance (singleton)

		Returns:
			UserRepository instance
		"""
		if self._user_repository is None:
			self._user_repository = UserRepository()
			logger.info("UserRepository instance created")
		return self._user_repository

	@lru_cache(maxsize=1)
	def user_service(self) -> UserService:
		"""
		Get user service instance (singleton)

		Returns:
			UserService instance with injected dependencies
		"""
		if self.user_service is None:
			# Dependency injection: UserService depends ou UserRepository abstraction
			self._user_service = UserService(self.user_repository())
			logger.info("UserService instance crated with injected dependencies")
		return self._user_service
