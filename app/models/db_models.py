"""
SQLAlchemy ORM models
Demonstrating Single Responsibility Principle (SRP)
Each model is responsible for database representation only
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def generate_uuid():
	"""Generate UUID as string for database storage"""
	return str(uuid4())


class UserDB(Base):
	"""
	SQLAlchemy model for User table

	SRP: Only responsible for database schema definition and ORM mapping
	This is separate from Pydantic models which handle validation
	"""

	__tablename__ = "users"

	id: Mapped[str] = mapped_column(
		String(36),
		primary_key=True,
		default=generate_uuid,
		doc="Unique user identifier (UUID as string)",
	)
	name: Mapped[str] = mapped_column(
		String(100), nullable=False, doc="User's full name"
	)
	email: Mapped[str] = mapped_column(
		String(255),
		nullable=False,
		unique=True,
		index=True,
		doc="User's email address (unique)",
	)
	created_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		default=datetime.utcnow,
		doc="Creation timestamp",
	)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime,
		nullable=False,
		default=datetime.utcnow,
		onupdate=datetime.utcnow,
		doc="Last update timestamp",
	)

	def __repr__(self) -> str:
		return f"<User(id={self.id}, name={self.name}, email={self.email})>"
