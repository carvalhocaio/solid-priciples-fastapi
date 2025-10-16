"""
Integration tests for complete user flow with real database
Following AAA (Arrange-Act-Assert) pattern
"""

import pytest

from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from tests.factories import create_user_data


@pytest.mark.integration
class TestUserRepositoryServiceIntegration:
	"""Test integration between repository and service with real database."""

	async def test_complete_user_crud_flow(self, test_db_session):
		"""
		GIVEN a repository and service with real database
		WHEN performing complete CRUD operations
		THEN all operations work correctly end-to-end
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		service = UserService(repository)

		# Act 1: Create user
		user_data = create_user_data(
			name="Integration Test User", email="integration@test.com"
		)
		created_user = await service.create(user_data)

		# Assert 1: User created
		assert created_user.id is not None
		assert created_user.name == "Integration Test User"
		assert created_user.email == "integration@test.com"

		# Act 2: Get user by id
		retrieved_user = await service.get_by_id(created_user.id)

		# Assert 2: User retrieved
		assert retrieved_user.id == created_user.id
		assert retrieved_user.email == created_user.email

		# Act 3: Update user
		from app.models.user import UserUpdate

		update_data = UserUpdate(name="Updated Name")
		updated_user = await service.update(created_user.id, update_data)

		# Assert 3: User updated
		assert updated_user.name == "Updated Name"
		assert updated_user.email == "integration@test.com"

		# Act 4: Get all users
		all_users, count = await service.get_all()

		# Assert 4: User in list
		assert count == 1
		assert len(all_users) == 1
		assert all_users[0].id == created_user.id

		# Act 5: Delete user
		delete_result = await service.delete(created_user.id)

		# Assert 5: User deleted
		assert delete_result is True

		# Act 6: Verify deletion
		all_users_after_delete, count_after = await service.get_all()

		# Assert 6: No users remain
		assert count_after == 0
		assert len(all_users_after_delete) == 0

	async def test_multiple_users_with_pagination(self, test_db_session):
		"""
		GIVEN multiple users in database
		WHEN retrieving users with pagination
		THEN correct pagination results are returned
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		service = UserService(repository)

		# Create 15 users
		created_users = []
		for i in range(15):
			user_data = create_user_data(email=f"user{i}@test.com")
			user = await service.create(user_data)
			created_users.append(user)

		# Act 1: Get first page
		page_1, total = await service.get_all(skip=0, limit=5)

		# Assert 1: First page correct
		assert len(page_1) == 5
		assert total == 15

		# Act 2: Get second page
		page_2, _ = await service.get_all(skip=5, limit=5)

		# Assert 2: Second page correct
		assert len(page_2) == 5

		# Act 3: Get last page
		page_3, _ = await service.get_all(skip=10, limit=5)

		# Assert 3: Last page correct
		assert len(page_3) == 5

		# Verify no duplicates across pages
		all_ids = [u.id for u in page_1 + page_2 + page_3]
		assert len(all_ids) == len(set(all_ids))

	async def test_sequential_user_creation(self, test_db_session):
		"""
		GIVEN multiple user creation requests
		WHEN creating users sequentially
		THEN all users are created without conflicts
		"""
		# Arrange
		repository = UserRepository(test_db_session)
		service = UserService(repository)

		# Act: Create users sequentially
		results = []
		for i in range(5):
			user_data = create_user_data(email=f"sequential{i}@test.com")
			user = await service.create(user_data)
			results.append(user)

		# Assert: All users created
		assert len(results) == 5
		assert all(user.id is not None for user in results)

		# Verify count
		all_users, count = await service.get_all()
		assert count == 5

		# Verify all emails are unique
		emails = [user.email for user in all_users]
		assert len(emails) == len(set(emails))
