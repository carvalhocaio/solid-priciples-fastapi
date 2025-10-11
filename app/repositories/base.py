"""
Base repository demonstrating Interface Segregation Principle (ISP)
and Open/Closed Principle (OCP)
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
	"""
	Abstract base repository following ISP and OCP principles

	ISP: Interface is focused and minimal
	OCP: Open for extension (new repository types) but closed for modification
	"""

	@abstractmethod
	async def create(self, entity: T) -> T:
		"""Create a new entity"""
		pass

	@abstractmethod
	async def get_by_id(self, entity_id: UUID) -> Optional[T]:
		"""Get entity by ID"""
		pass

	@abstractmethod
	async def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
		"""Get all entities with pagination"""
		pass

	@abstractmethod
	async def update(self, entity_id: UUID, entity_data: dict) -> Optional[T]:
		"""Update an entity"""
		pass

	@abstractmethod
	async def delete(self, entity_id: UUID) -> bool:
		"""Delete an entity"""
		pass

	@abstractmethod
	async def count(self) -> int:
		"""Get total count of entities"""
		pass
