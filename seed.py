"""
Seed script to generate 21 users using Faker library
"""
import asyncio
import logging

from faker import Faker

from app.database import init_db, close_db, AsyncSessionLocal
from app.dependencies.container import Container
from app.models.user import UserCreate

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def seed_users(num_users: int = 21) -> None:
	"""
	Seed database with fake users

	Args:
		num_users: Number of users to create (default: 21)
	"""
	logger.info(f"Starting seed process for {num_users} users...")

	# Initialize database
	await init_db()

	# Initialize Faker
	fake = Faker()

	# Initialize container
	container = Container()

	created_count = 0
	failed_count = 0

	# Create database session
	async with AsyncSessionLocal() as session:
		try:
			# Get user service with session
			user_service = container.user_service(session)

			for i in range(num_users):
				try:
					# Generate fake user data
					user_data = UserCreate(
						name=fake.name(),
						email=fake.unique.email(),
					)

					# Create user
					user = await user_service.create(user_data)
					created_count += 1

					logger.info(
						f"[{i + 1}/{num_users}] User created: {user.name} ({user.email})"
					)

				except Exception as e:
					failed_count += 1
					logger.error(f"[{i + 1}/{num_users}] Failed to create user: {e}")

			# Commit all changes
			await session.commit()
			logger.info("All changes committed to database")

		except Exception as e:
			await session.rollback()
			logger.error(f"Transaction rolled back due to error: {e}")
			raise

	logger.info(
		f"Seed process completed! Created: {created_count}, Failed: {failed_count}"
	)


async def main():
	"""Main entry point for the seed script"""
	try:
		await seed_users(21)
	except Exception as e:
		logger.error(f"Seed process failed: {e}")
		raise
	finally:
		# Close database connections
		await close_db()


if __name__ == "__main__":
	asyncio.run(main())
