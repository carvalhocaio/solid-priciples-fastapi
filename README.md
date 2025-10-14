# FastAPI SOLID CRUD API

This project demonstrates how to implement SOLID principles in a FastAPI application with CRUD operations for users.

## SOLID Principles Implementation

### 1. Single Responsibility Principle (SRP)
Each class has a single, well-defined responsibility:

- **UserModel**: Only responsible for data representation and validation
- **UserRepository**: Only responsible for data persistence operations
- **UserService**: Only responsible for business logic
- **UserController**: Only responsible for HTTP request/response handling
- **Container**: Only responsible for dependency injection

### 2. Open/Closed Principle (OCP)
The system is open for extension but closed for modification:

- **BaseRepository**: Abstract class that can be extended for different data sources (database, file, API) without modifying existing code
- **BaseService**: Abstract class that can be extended for different business logic implementations
- **Repository Pattern**: New repository implementations can be added without changing service layer

### 3. Liskov Substitution Principle (LSP)
Derived classes can replace base classes without breaking functionality:

- Any implementation of `BaseRepository` can replace another implementation
- Any implementation of `BaseService` can replace another implementation
- The dependency injection system ensures proper substitutability

### 4. Interface Segregation Principle (ISP)
Interfaces are focused and clients don't depend on methods they don't use:

- **BaseRepository**: Contains only essential CRUD operations
- **BaseService**: Contains only business logic operations
- No class is forced to implement unused methods

### 5. Dependency Inversion Principle (DIP)
High-level modules depend on abstractions, not concretions:

- **UserService** depends on `BaseRepository` abstraction, not concrete `UserRepository`
- **UserController** depends on `BaseService` abstraction, not concrete `UserService`
- **Container** manages dependency injection, ensuring loose coupling

## Project Structure

```
/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
└── app/
    ├── __init__.py
    ├── models/                     # Data models (SRP)
    │   ├── __init__.py
    │   └── user.py                 # User Pydantic models
    ├── repositories/               # Data access layer (SRP, OCP, LSP)
    │   ├── __init__.py
    │   ├── base.py                 # Abstract base repository
    │   └── user_repository.py      # User repository implementation
    ├── services/                   # Business logic layer (SRP, OCP, LSP)
    │   ├── __init__.py
    │   ├── base.py                 # Abstract base service
    │   └── user_service.py         # User service implementation
    ├── controllers/                # HTTP handling layer (SRP)
    │   ├── __init__.py
    │   └── user_controller.py      # User API endpoints
    ├── dependencies/               # Dependency injection (DIP)
    │   ├── __init__.py
    │   └── container.py            # DI container
    └── exceptions/                 # Custom exceptions (SRP)
        ├── __init__.py
        └── user_exceptions.py      # User-specific exceptions
```

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Create User
```http
POST /api/v1/users
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john.doe@example.com"
}
```

### Get User by ID
```http
GET /api/v1/users/{user_id}
```

### Get All Users (with pagination)
```http
GET /api/v1/users?page=1&per_page=10
```

### Update User
```http
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
    "name": "Jane Doe",
    "email": "jane.doe@example.com"
}
```

### Delete User
```http
DELETE /api/v1/users/{user_id}
```

## Example Usage

### Creating a User
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
     -H "Content-Type: application/json" \
     -d '{
         "name": "John Doe",
         "email": "john.doe@example.com"
     }'
```

### Getting All Users
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&per_page=5"
```

## Benefits of SOLID Implementation

1. **Maintainability**: Each class has a single responsibility, making it easier to understand and modify
2. **Testability**: Dependencies are injected, making unit testing straightforward
3. **Extensibility**: New features can be added without modifying existing code
4. **Flexibility**: Different implementations can be swapped easily (e.g., database repository)
5. **Loose Coupling**: High-level modules don't depend on low-level implementation details
