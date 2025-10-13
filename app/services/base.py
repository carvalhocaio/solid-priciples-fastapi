"""
Base service demonstration Interface Segregation Principle (ISP)
and Open/Closed Principles (OCP)
"""

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar
from uuid import UUID

T = TypeVar("T")
CreateT = TypeVar("CreateT")
UpdateT = TypeVar("UpdateT")


class BaseService(Generic[T, CreateT, UpdateT], ABC):
	"""
	Abstract base service following ISP and OCP principles

	ISP: Interface is focused on business operations
	OCP: Open for extension (new service types) but closed for modification
	"""

	@abstractmethod
	async def create(self, entity_data: CreateT) -> T:
		"""Create a new entity with business logic"""
		pass

	@abstractmethod
	async def get_by_id(self, entity_id: UUID) -> T:
		"""Get entity by ID with business logic"""
		pass

	@abstractmethod
	async def get_all(
		self, skip: int = 0, limit: int = 10
	) -> tuple[List[T], int]:
		"""Get all entities with pagination and total count"""
		pass

	@abstractmethod
	async def update(self, entity_id: UUID, entity_data: UpdateT) -> T:
		"""Update an entity with business logic"""
		pass

	@abstractmethod
	async def delete(self, entity_id: UUID) -> bool:
		"""Delete an entity with business logic"""
		pass
