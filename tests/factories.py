"""
Factory Boy factories for test data generation
"""

from datetime import datetime
from uuid import uuid4

import factory
from factory import LazyFunction

from app.models.db_models import UserDB
from app.models.user import User, UserCreate, UserUpdate


class UserDBFactory(factory.Factory):
	"""Factory for UserDB SQLAlchemy model."""

	class Meta:
		model = UserDB

	id = LazyFunction(lambda: str(uuid4()))
	name = factory.Faker("name")
	email = factory.Faker("email")
	created_at = LazyFunction(datetime.utcnow)
	updated_at = LazyFunction(datetime.utcnow)


class UserFactory(factory.Factory):
	"""Factory for User Pydantic model."""

	class Meta:
		model = User

	id = LazyFunction(uuid4)
	name = factory.Faker("name")
	email = factory.Faker("email")
	created_at = LazyFunction(datetime.utcnow)
	updated_at = LazyFunction(datetime.utcnow)


class UserCreateFactory(factory.Factory):
	"""Factory for UserCreate Pydantic model."""

	class Meta:
		model = UserCreate

	name = factory.Faker("name")
	email = factory.Faker("email")


class UserUpdateFactory(factory.Factory):
	"""Factory for UserUpdate Pydantic model."""

	class Meta:
		model = UserUpdate

	name = factory.Faker("name")
	email = factory.Faker("email")


# Helper functions for common test scenarios
def create_user_data(**kwargs) -> UserCreate:
	"""Create UserCreate instance with optional overrides."""
	return UserCreateFactory(**kwargs)


def create_user(**kwargs) -> User:
	"""Create User instance with optional overrides."""
	return UserFactory(**kwargs)


def create_user_db(**kwargs) -> UserDB:
	"""Create UserDB instance with optional overrides."""
	return UserFactory(**kwargs)
