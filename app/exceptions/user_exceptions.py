"""
Custom exceptions for user operations
Demonstrates Single Responsibility Principle (SRP)
"""


class UserNotFoundError(Exception):
	"""
	Exception raised when a user is not found

	SRP: Only responsible for representing "user not found" error state
	"""

	def __init__(self, message: str = "User not found"):
		self.message = message
		super().__init__(self.message)


class UserAlreadyExistsError(Exception):
	"""
	Exception raised when trying to create a user that already exists

	SRP: Only responsible for representing "user already exists" error state
	"""

	def __init__(self, message: str = "User already exists"):
		self.message = message
		super().__init__(self.message)
