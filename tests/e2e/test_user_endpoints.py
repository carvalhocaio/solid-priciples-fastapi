"""
End-to-End tests for user API endpoints
Following AAA (Arrange-Act-Assert) pattern
"""

import pytest
from httpx import AsyncClient

from tests.factories import create_user_data


@pytest.mark.e2e
class TestUserEndpointsCreate:
	"""Test POST /api/v1/users endpoint."""

	async def test_create_user_success(self, client: AsyncClient):
		"""
		GIVEN a valid user payload
		WHEN posting to /api/v1/users
		THEN user is created and 201 status is returned
		"""
		# Arrange
		payload = {"name": "John Doe", "email": "john.doe@example.com"}

		# Act
		response = await client.post("/api/v1/users", json=payload)

		# Assert
		assert response.status_code == 201
		data = response.json()
		assert data["name"] == "John Doe"
		assert data["email"] == "john.doe@example.com"
		assert "id" in data
		assert "created_at" in data
		assert "updated_at" in data

	async def test_create_user_invalid_email(self, client: AsyncClient):
		"""
		GIVEN an invalid email format
		WHEN posting to /api/v1/users
		THEN 422 validation error is returned
		"""
		# Arrange
		payload = {"name": "John Doe", "email": "invalid-email"}

		# Act
		response = await client.post("/api/v1/users", json=payload)

		# Assert
		assert response.status_code == 422

	async def test_create_user_missing_required_fields(
		self, client: AsyncClient
	):
		"""
		GIVEN a payload missing required fields
		WHEN posting to /api/v1/users
		THEN 422 validation error is returned
		"""
		# Arrange
		payload = {
			"name": "John Doe"
			# missing email
		}

		# Act
		response = await client.post("/api/v1/users", json=payload)

		# Assert
		assert response.status_code == 422

	async def test_create_user_duplicate_email(self, client: AsyncClient):
		"""
		GIVEN an existing user with an email
		WHEN creating another user with same email
		THEN 409 conflict error is returned
		"""
		# Arrange
		payload = {"name": "John Doe", "email": "duplicate@example.com"}
		await client.post("/api/v1/users", json=payload)

		# Act
		response = await client.post("/api/v1/users", json=payload)

		# Assert
		assert response.status_code == 409


@pytest.mark.e2e
class TestUserEndpointsGet:
	"""Test GET /api/v1/users endpoints."""

	async def test_get_user_by_id_success(self, client: AsyncClient):
		"""
		GIVEN an existing user
		WHEN getting user by id
		THEN user data is returned with 200 status
		"""
		# Arrange - create user first
		create_payload = {"name": "Jane Doe", "email": "jane.doe@example.com"}
		create_response = await client.post(
			"/api/v1/users", json=create_payload
		)
		user_id = create_response.json()["id"]

		# Act
		response = await client.get(f"/api/v1/users/{user_id}")

		# Assert
		assert response.status_code == 200
		data = response.json()
		assert data["id"] == user_id
		assert data["name"] == "Jane Doe"
		assert data["email"] == "jane.doe@example.com"

	async def test_get_user_by_id_not_found(self, client: AsyncClient):
		"""
		GIVEN a non-existent user id
		WHEN getting user by id
		THEN 404 not found is returned
		"""
		# Arrange
		non_existent_id = "00000000-0000-0000-0000-000000000000"

		# Act
		response = await client.get(f"/api/v1/users/{non_existent_id}")

		# Assert
		assert response.status_code == 404

	async def test_get_all_users_empty(self, client: AsyncClient):
		"""
		GIVEN no users in database
		WHEN getting all users
		THEN empty list is returned with pagination info
		"""
		# Arrange - no users

		# Act
		response = await client.get("/api/v1/users")

		# Assert
		assert response.status_code == 200
		data = response.json()
		assert data["users"] == []
		assert data["total"] == 0
		assert data["page"] == 1
		assert data["per_page"] == 10

	async def test_get_all_users_with_data(self, client: AsyncClient):
		"""
		GIVEN multiple users in database
		WHEN getting all users
		THEN users list is returned with correct pagination
		"""
		# Arrange - create 3 users
		for i in range(3):
			payload = {"name": f"User {i}", "email": f"user{i}@example.com"}
			await client.post("/api/v1/users", json=payload)

		# Act
		response = await client.get("/api/v1/users")

		# Assert
		assert response.status_code == 200
		data = response.json()
		assert len(data["users"]) == 3
		assert data["total"] == 3
		assert data["page"] == 1
		assert data["per_page"] == 10
		assert data["total_pages"] == 1

	async def test_get_all_users_with_pagination(self, client: AsyncClient):
		"""
		GIVEN multiple users in database
		WHEN getting users with pagination parameters
		THEN correct page is returned
		"""
		# Arrange - create 15 users
		for i in range(15):
			payload = {
				"name": f"User {i}",
				"email": f"paginated{i}@example.com",
			}
			await client.post("/api/v1/users", json=payload)

		# Act
		response = await client.get("/api/v1/users?page=2&per_page=5")

		# Assert
		assert response.status_code == 200
		data = response.json()
		assert len(data["users"]) == 5
		assert data["total"] == 15
		assert data["page"] == 2
		assert data["per_page"] == 5
		assert data["total_pages"] == 3


@pytest.mark.e2e
class TestUserEndpointsUpdate:
	"""Test PUT /api/v1/users/{user_id} endpoint."""

	async def test_update_user_success(self, client: AsyncClient):
		"""
		GIVEN an existing user
		WHEN updating user data
		THEN user is updated and 200 status is returned
		"""
		# Arrange - create user first
		create_payload = {
			"name": "Original Name",
			"email": "original@example.com",
		}
		create_response = await client.post(
			"/api/v1/users", json=create_payload
		)
		user_id = create_response.json()["id"]

		update_payload = {
			"name": "Updated Name",
			"email": "updated@example.com",
		}

		# Act
		response = await client.put(
			f"/api/v1/users/{user_id}", json=update_payload
		)

		# Assert
		assert response.status_code == 200
		data = response.json()
		assert data["id"] == user_id
		assert data["name"] == "Updated Name"
		assert data["email"] == "updated@example.com"

	async def test_update_user_partial(self, client: AsyncClient):
		"""
		GIVEN an existing user
		WHEN updating only some fields
		THEN only specified fields are updated
		"""
		# Arrange
		create_payload = {
			"name": "Original Name",
			"email": "original@example.com",
		}
		create_response = await client.post(
			"/api/v1/users", json=create_payload
		)
		user_id = create_response.json()["id"]

		update_payload = {
			"name": "New Name"
			# email not included
		}

		# Act
		response = await client.put(
			f"/api/v1/users/{user_id}", json=update_payload
		)

		# Assert
		assert response.status_code == 200
		data = response.json()
		assert data["name"] == "New Name"
		assert data["email"] == "original@example.com"  # unchanged

	async def test_update_user_not_found(self, client: AsyncClient):
		"""
		GIVEN a non-existent user id
		WHEN updating user
		THEN 404 not found is returned
		"""
		# Arrange
		non_existent_id = "00000000-0000-0000-0000-000000000000"
		update_payload = {"name": "New Name"}

		# Act
		response = await client.put(
			f"/api/v1/users/{non_existent_id}", json=update_payload
		)

		# Assert
		assert response.status_code == 404


@pytest.mark.e2e
class TestUserEndpointsDelete:
	"""Test DELETE /api/v1/users/{user_id} endpoint."""

	async def test_delete_user_success(self, client: AsyncClient):
		"""
		GIVEN an existing user
		WHEN deleting the user
		THEN 204 no content is returned
		"""
		# Arrange - create user first
		create_payload = {"name": "To Delete", "email": "delete@example.com"}
		create_response = await client.post(
			"/api/v1/users", json=create_payload
		)
		user_id = create_response.json()["id"]

		# Act
		response = await client.delete(f"/api/v1/users/{user_id}")

		# Assert
		assert response.status_code == 204

		# Verify user is deleted
		get_response = await client.get(f"/api/v1/users/{user_id}")
		assert get_response.status_code == 404

	async def test_delete_user_not_found(self, client: AsyncClient):
		"""
		GIVEN a non-existent user id
		WHEN deleting user
		THEN 404 not found is returned
		"""
		# Arrange
		non_existent_id = "00000000-0000-0000-0000-000000000000"

		# Act
		response = await client.delete(f"/api/v1/users/{non_existent_id}")

		# Assert
		assert response.status_code == 404


@pytest.mark.e2e
class TestUserEndpointsCompleteFlow:
	"""Test complete user lifecycle through API."""

	async def test_complete_user_lifecycle(self, client: AsyncClient):
		"""
		GIVEN a clean database
		WHEN performing complete user lifecycle operations
		THEN all operations succeed in sequence
		"""
		# Arrange
		initial_list = await client.get("/api/v1/users")
		initial_count = initial_list.json()["total"]

		# Act 1: Create user
		create_payload = {
			"name": "Lifecycle User",
			"email": "lifecycle@example.com",
		}
		create_response = await client.post(
			"/api/v1/users", json=create_payload
		)

		# Assert 1: User created
		assert create_response.status_code == 201
		user_id = create_response.json()["id"]

		# Act 2: Get user
		get_response = await client.get(f"/api/v1/users/{user_id}")

		# Assert 2: User retrieved
		assert get_response.status_code == 200
		assert get_response.json()["email"] == "lifecycle@example.com"

		# Act 3: Update user
		update_response = await client.put(
			f"/api/v1/users/{user_id}", json={"name": "Updated Lifecycle"}
		)

		# Assert 3: User updated
		assert update_response.status_code == 200
		assert update_response.json()["name"] == "Updated Lifecycle"

		# Act 4: Verify in list
		list_response = await client.get("/api/v1/users")

		# Assert 4: User in list
		assert list_response.status_code == 200
		assert list_response.json()["total"] == initial_count + 1

		# Act 5: Delete user
		delete_response = await client.delete(f"/api/v1/users/{user_id}")

		# Assert 5: User deleted
		assert delete_response.status_code == 204

		# Act 6: Verify deletion
		final_get = await client.get(f"/api/v1/users/{user_id}")
		final_list = await client.get("/api/v1/users")

		# Assert 6: User gone
		assert final_get.status_code == 404
		assert final_list.json()["total"] == initial_count
