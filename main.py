"""
FastAPI CRUD API demonstrating SOLID principles
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.controllers.user_controller import UserController
from app.database import init_db, close_db
from app.dependencies.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
	"""
	Application lifespan manager
	Handles startup and shutdown events
	"""
	# Startup: Initialize database
	await init_db()
	yield
	# Shutdown: Close database connections
	await close_db()


def create_app() -> FastAPI:
	"""
	Application factory following Dependency Inversion Principle
	"""
	app = FastAPI(
		title="FastAPI SOLID CRUD",
		description="A FastAPI application demonstrating SOLID principles with User CRUD operations",
		version="1.0.0",
		lifespan=lifespan
	)

	# Initialize dependency container
	container = Container()

	# Include routers with dependency injection
	user_controller = UserController(container)
	app.include_router(user_controller.router, prefix="/api/v1", tags=["users"])

	return app

app = create_app()

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
