"""
User models demonstrating Single Responsibility Principle (SRP)
Eah model has a single, well-defined purpose
"""

from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
	"""Base user model with common fields"""

	name: str = Field(
		..., min_length=1, max_length=100, description="User's full name"
	)
	email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
	"""
	Model for user creation requests
	SRP: Only responsible for validating user creation data
	"""

	pass


class UserUpdate(BaseModel):
	"""
	Model for user update requests
	SRP: Only responsible for validating user update data
	"""

	name: Optional[str] = Field(
		None, min_length=1, max_length=100, description="User's full name"
	)
	email: Optional[EmailStr] = Field(None, description="User's email address")


class User(UserBase):
	"""
	Complete user model with all fields
	SRP: Only responsible for representing user data
	"""

	id: UUID = Field(
		default_factory=uuid4, description="Unique user identifier"
	)
	created_at: datetime = Field(
		default_factory=lambda: datetime.now(UTC),
		description="Creation timestamp",
	)
	updated_at: datetime = Field(
		default_factory=lambda: datetime.now(UTC),
		description="Last update timestamp",
	)

	model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
	"""
	Model for user API response
	SRP: Only responsible for API response formatting
	"""

	id: UUID
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
	"""
	Model for paginated user list responses
	"""

	users: list[UserResponse]
	total: int
	page: int
	per_page: int
	total_pages: int
