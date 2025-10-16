"""
Helper functions for tests
Utilities to make testing easier and more consistent
"""
import asyncio
from typing import Any, Callable, List
from uuid import UUID

from httpx import AsyncClient

from app.models.user import UserCreate


async def create_multiple_users(
	client: AsyncClient, count: int, email_prefix: str = "user"
) -> List[dict]:
	"""
	Helper to create multiple users via API.

	Args:
		client: HTTP client
		count: Number of users to create
		email_prefix: Prefix for email addresses

	Returns:
		List of created user data
	"""
	users = []
	for i in range(count):
		payload = {
			"name": f"Test User {i}",
			"email": f"{email_prefix}{i}@example.com",
		}
		response = await client.post("/api/v1/users", json=payload)
		if response.status_code == 201:
			users.append(response.json())
	return users


async def cleanup_users(client: AsyncClient, user_ids: List[UUID | str]) -> None:
	"""
	Helper to cleanup multiple users.

	Args:
		client: HTTP client
		user_ids: List of user IDs to delete
	"""
	for user_id in user_ids:
		await client.delete(f"/api/v1/users/{user_id}")


async def wait_for_condition(
	condition: Callable[[], bool],
	timeout: float = 5.0,
	interval: float = 0.1,
) -> bool:
	"""
	Wait for a condition to become true.

	Args:
		condition: Function that returns bool
		timeout: Maximum time to wait in seconds
		interval: Check interval in seconds

	Returns:
		True if condition met, False if timeout
	"""
	elapsed = 0.0
	while elapsed < timeout:
		if condition():
			return True
		await asyncio.sleep(interval)
		elapsed += interval
	return False


def assert_user_data_matches(
	actual: dict, expected: UserCreate, check_id: bool = True
) -> None:
	"""
	Assert that user data matches expected values.

	Args:
		actual: Actual user data dictionary
		expected: Expected UserCreate data
		check_id: Whether to check for ID presence
	"""
	assert actual["name"] == expected.name
	assert actual["email"] == expected.email

	if check_id:
		assert "id" in actual
		assert actual["id"] is not None

	assert "created_at" in actual
	assert "updated_at" in actual


def assert_pagination_data(
	data: dict,
	expected_total: int,
	expected_page: int,
	expected_per_page: int,
) -> None:
	"""
	Assert pagination metadata is correct.

	Args:
		data: Response data with pagination
		expected_total: Expected total count
		expected_page: Expected current page
		expected_per_page: Expected items per page
	"""
	assert data["total"] == expected_total
	assert data["page"] == expected_page
	assert data["per_page"] == expected_per_page

	# Calculate expected total_pages
	expected_total_pages = (
		(expected_total + expected_per_page - 1) // expected_per_page
		if expected_total > 0
		else 1
	)
	assert data["total_pages"] == expected_total_pages


def assert_error_response(
	response_data: dict, expected_status: int, error_keyword: str = None
) -> None:
	"""
	Assert error response format.

	Args:
		response_data: Response data
		expected_status: Expected HTTP status code
		error_keyword: Optional keyword to check in error message
	"""
	assert "detail" in response_data or "message" in response_data

	if error_keyword:
		detail = response_data.get("detail", response_data.get("message", ""))
		assert error_keyword.lower() in str(detail).lower()


async def batch_create_users(
	client: AsyncClient, users_data: List[dict]
) -> List[dict]:
	"""
	Create multiple users in batch.

	Args:
		client: HTTP client
		users_data: List of user data dictionaries

	Returns:
		List of created users
	"""
	tasks = [
		client.post("/api/v1/users", json=user_data)
		for user_data in users_data
	]
	responses = await asyncio.gather(*tasks, return_exceptions=True)

	created_users = []
	for response in responses:
		if not isinstance(response, Exception) and response.status_code == 201:
			created_users.append(response.json())

	return created_users


def generate_test_email(prefix: str = "test") -> str:
	"""
	Generate a unique test email.

	Args:
		prefix: Email prefix

	Returns:
		Unique email address
	"""
	from uuid import uuid4

	return f"{prefix}_{uuid4().hex[:8]}@example.com"


def generate_test_users_data(count: int) -> List[dict]:
	"""
	Generate test user data.

	Args:
		count: Number of users to generate

	Returns:
		List of user data dictionaries
	"""
	return [
		{
			"name": f"Test User {i}",
			"email": generate_test_email(f"user{i}"),
		}
		for i in range(count)
	]


class TestDataBuilder:
	"""
	Builder pattern for test data.
	Useful for creating complex test scenarios.
	"""

	def __init__(self):
		self._users_data = []

	def add_user(self, name: str = None, email: str = None) -> "TestDataBuilder":
		"""Add a user to the builder."""
		user_data = {
			"name": name or f"User {len(self._users_data)}",
			"email": email or generate_test_email(),
		}
		self._users_data.append(user_data)
		return self

	def add_users(self, count: int) -> "TestDataBuilder":
		"""Add multiple users to the builder."""
		for _ in range(count):
			self.add_user()
		return self

	def build(self) -> List[dict]:
		"""Build and return the test data."""
		return self._users_data

	def reset(self) -> "TestDataBuilder":
		"""Reset the builder."""
		self._users_data = []
		return self


class AsyncTestTimer:
	"""
	Context manager for timing async operations in tests.

	Example:
		async with AsyncTestTimer() as timer:
			await some_operation()
		assert timer.elapsed < 1.0  # Verify operation was fast enough
	"""

	def __init__(self):
		self.start_time = None
		self.end_time = None
		self.elapsed = None

	async def __aenter__(self):
		import time

		self.start_time = time.time()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		import time

		self.end_time = time.time()
		self.elapsed = self.end_time - self.start_time
		return False


# Performance test helpers
def assert_performance(elapsed: float, max_time: float, operation: str = "Operation"):
	"""
	Assert that an operation completed within expected time.

	Args:
		elapsed: Actual elapsed time
		max_time: Maximum allowed time
		operation: Description of the operation
	"""
	assert (
		elapsed <= max_time
	), f"{operation} took {elapsed:.2f}s, expected <={max_time}s"


# Comparison helpers
def dict_contains(superset: dict, subset: dict) -> bool:
	"""
	Check if superset contains all key-value pairs from subset.

	Args:
		superset: Dictionary to check
		subset: Dictionary with expected values

	Returns:
		True if superset contains subset
	"""
	return all(
		key in superset and superset[key] == value for key, value in subset.items()
	)


def assert_dict_contains(superset: dict, subset: dict) -> None:
	"""
	Assert that superset contains all key-value pairs from subset.

	Args:
		superset: Dictionary to check
		subset: Dictionary with expected values
	"""
	for key, value in subset.items():
		assert key in superset, f"Key '{key}' not found in response"
		assert (
			superset[key] == value
		), f"Expected {key}={value}, got {key}={superset[key]}"
