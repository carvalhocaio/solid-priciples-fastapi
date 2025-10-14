"""
FastAPI CRUD API demonstrating SOLID principles
"""
from fastapi import FastAPI

from app.controllers.user_controller import UserController
from app.dependencies.container import Container


def create_app() -> FastAPI:
	"""
	Application factory following Dependency Inversion Principle
	"""
	app = FastAPI(
		title="FastAPI SOLID CRUD",
		description="A FastAPI application demonstrating SOLID principles with User CRUD operations",
		version="1.0.0"
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
