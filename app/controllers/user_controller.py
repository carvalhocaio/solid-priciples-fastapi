"""
User controller demonstrating Single Responsibility Principle (SRP)
and Dependency Inversion Principle (DIP)
"""

import logging
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.dependencies.container import Container
from app.exceptions.user_exceptions import (
	UserAlreadyExistsError,
	UserNotFoundError,
)
from app.models.user import (
	UserCreate,
	UserListResponse,
	UserResponse,
	UserUpdate,
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class UserController:
	"""
	User controller handling HTTP requests and responses

	SRP: Only responsible for HTTP request/response handling
	DIP: Depends on abstraction (BaseService) not concrete implementation
	"""

	def __init__(self, container: Container):
		"""
		Initialize user controller with dependency injection

		Args:
			container: Dependency injection container
		"""
		self.router = APIRouter()
		self._container = container
		self._setup_routes()
		logger.info("UserController initialized")

	def _setup_routes(self):
		"""Setup API routes"""
		self.router.add_api_route(
			"/users",
			self.create_user,
			methods=["POST"],
			status_code=status.HTTP_201_CREATED,
			response_model=UserResponse,
			summary="Create a new user",
			description="Create a new user with name and email",
		)

		self.router.add_api_route(
			"/users/{user_id}",
			self.get_user,
			methods=["GET"],
			response_model=UserResponse,
			summary="Get user by ID",
			description="Retrieve a user by their unique identifier",
		)

		self.router.add_api_route(
			"/users",
			self.get_users,
			methods=["GET"],
			response_model=UserListResponse,
			summary="Get all users",
			description="Retrieve all users with pagination support",
		)

		self.router.add_api_route(
			"/users/{user_id}",
			self.update_user,
			methods=["PUT"],
			response_model=UserResponse,
			summary="Update user",
			description="Update an existing user's information",
		)

		self.router.add_api_route(
			"/users/{user_id}",
			self.delete_user,
			methods=["DELETE"],
			status_code=status.HTTP_204_NO_CONTENT,
			summary="Delete user",
			description="Delete a user by their unique identifier",
		)

	async def create_user(
		self,
		user_data: UserCreate,
		user_service: Annotated[
			BaseService, Depends(lambda: self._container.user_service())
		],
	) -> UserResponse:
		"""
		Create a new user

		Args:
			user_data: User creation data
			user_service: Injected user service

		Returns:
			Created user response

		Raises:
			HTTPException: If user already exists or validation fails
		"""
		try:
			logger.info(f"Creating yser via API: {user_data.email}")
			user = await user_service.create(user_data)
			return UserResponse.model_validate(user)
		except UserAlreadyExistsError as e:
			logger.warning(f"User creation failed: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT, detail=str(e)
			)
		except Exception as e:
			logger.error(f"Unexpected error creating user: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Internal server error",
			)

	async def get_user(
		self,
		user_id: UUID,
		user_service: Annotated[
			BaseService, Depends(lambda: self._container.user_service())
		],
	) -> UserResponse:
		"""
		Get user by ID

		Args:
			user_id: User ID
			user_service: Injected user service

		Returns:
			User response

		Raises:
			HttpException: If user is not found
		"""
		try:
			logger.info(f"Getting user via API: {user_id}")
			user = await user_service.get_by_id(user_id)
			return UserResponse.model_validate(user)
		except UserNotFoundError as e:
			logger.warning(f"User not found: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
			)
		except Exception as e:
			logger.error(f"Unexpected error getting user: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Internal server error",
			)

	async def get_users(
		self,
		page: Annotated[int, Query(ge=1, description="Page number")] = 1,
		per_page: Annotated[
			int, Query(ge=1, le=100, description="Items per page")
		] = 10,
		user_service: Annotated[
			BaseService, Depends(lambda: self._container.user_service())
		] = None,
	) -> UserListResponse:
		"""
		Get all users with pagination

		Args:
			page: Page number (1-indexed)
			per_page: Items per page
			user_service: Injected user service

		Returns:
			Paginated user list response
		"""
		try:
			skip = (page - 1) * per_page
			logger.info(
				f"Getting users via API: page={page}, per_page={per_page}"
			)

			users, total_count = await user_service.get_all(skip, per_page)
			total_pages = (
				ceil(total_count / per_page) if total_count > 0 else 1
			)

			return UserListResponse(
				users=[UserResponse.model_validate(user) for user in users],
				total=total_count,
				page=page,
				per_page=per_page,
				total_pages=total_pages,
			)
		except Exception as e:
			logger.error(f"Unexpected error getting users: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Internal server error",
			)

	async def update_user(
		self,
		user_id: UUID,
		user_data: UserUpdate,
		user_service: Annotated[
			BaseService, Depends[lambda: self._container.user_service()]
		],
	) -> UserResponse:
		"""
		Update user

		Args:
			user_id: User ID
			user_data: User update data
			user_service: Injected user service

		Returns:
			Updated user response

		Raises:
			HttpException: If user is not found or email already exists
		"""
		try:
			logger.info(f"Updating user via API: {user_id}")
			user = await user_service.update(user_id, user_data)
			return UserResponse.model_validate(user)
		except UserNotFoundError as e:
			logger.warning(f"User found for update: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
			)
		except UserAlreadyExistsError as e:
			logger.warning(f"User update failed: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT, detail=str(e)
			)
		except Exception as e:
			logger.error(f"Unexpected error updating user: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Internal server error",
			)

	async def delete_user(
		self,
		user_id: UUID,
		user_service: Annotated[
			BaseService, Depends(lambda: self._container.user_service())
		],
	) -> JSONResponse:
		"""
		Delete user

		Args:
			user_id: User ID
			user_service: Injected user service

		Returns:
			Empty response with 204 status

		Raises:
			HttpException: If user is not found
		"""
		try:
			logger.info(f"Deleting user via API: {user_id}")
			await user_service.delete(user_id)
			return JSONResponse(
				status_code=status.HTTP_204_NO_CONTENT, content=None
			)
		except UserNotFoundError as e:
			logger.warning(f"User not found for deletion: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
			)
		except Exception as e:
			logger.error(f"Unexpected error deleting user: {str(e)}")
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Internal server error",
			)
