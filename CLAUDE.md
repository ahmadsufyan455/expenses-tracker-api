# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
uvicorn app.main:app --reload
```

### Testing
```bash
# Run all tests
python run_tests.py all

# Run specific test modules
python run_tests.py auth
python run_tests.py budgets
python run_tests.py categories
python run_tests.py transactions
python run_tests.py user

# Run with coverage
python run_tests.py coverage

# Run with verbose output
python run_tests.py verbose

# Using pytest directly
pytest tests/
pytest tests/test_auth_integration.py -v
pytest --cov=app --cov-report=html
```

### Code Formatting and Linting
The project uses several code quality tools available in requirements.txt:
- `black` - Code formatting
- `autopep8` - PEP8 compliance
- `yapf` - Code formatting

### Database Management
```bash
# Create and run migrations (if Alembic is configured)
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Architecture Overview

This is a **FastAPI-based expense tracking API** built with a clean architecture pattern:

### Core Architecture Layers
1. **API Layer** (`app/api/v1/`) - REST endpoint handlers
2. **Service Layer** (`app/services/`) - Business logic implementation
3. **Repository Layer** (`app/repositories/`) - Data access abstraction
4. **Model Layer** (`app/models/`) - SQLAlchemy database models

### Key Architectural Patterns
- **Dependency Injection** - FastAPI's built-in DI system manages dependencies
- **Repository Pattern** - All database operations go through repository classes that inherit from `BaseRepository`
- **Service Pattern** - Business logic is encapsulated in service classes
- **Enum-based Messages** - All response messages are defined as enums in `app/constants/messages.py`
- **Standardized Responses** - Uses `SuccessResponse` model for consistent API responses

### Business Logic Constraints
- **Budget Enforcement** - Expense transactions require an active budget for the category in the current month
- **User Isolation** - All operations are scoped to the authenticated user
- **Data Integrity** - One budget per category per month (enforced by database constraints)

### Database Models Relationships
- `User` → has many → `Category`, `Budget`, `Transaction`
- `Category` → has many → `Budget`, `Transaction`
- `Budget` → belongs to → `User`, `Category` (unique constraint on user_id, category_id, month)
- `Transaction` → belongs to → `User`, `Category`

### Authentication & Security
- **JWT-based authentication** using `python-jose`
- **Password hashing** with `bcrypt` via `passlib`
- **Protected routes** require valid Bearer token in Authorization header
- **User context injection** through `get_current_user` dependency

### Environment Configuration
Uses Pydantic Settings with `.env` file support. Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing secret
- `ALGORITHM` - JWT algorithm (typically HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

### Testing Strategy
- **Integration tests only** - No unit tests, focuses on full HTTP request/response testing
- **In-memory SQLite** - Each test uses a fresh database instance
- **Real authentication flow** - Tests include JWT token generation and validation
- **Business logic validation** - Tests verify budget enforcement and other constraints

### File Structure Conventions
- Models use SQLAlchemy with declarative base
- Schemas are Pydantic models for request/response validation
- Services contain business logic and coordinate between repositories
- Repositories handle all database operations
- API routes are thin controllers that delegate to services

### Key Dependencies to Know
- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - Database ORM (uses modern async-compatible syntax)
- **Pydantic v2** - Data validation and settings management
- **PostgreSQL** - Primary database (with psycopg2-binary driver)
- **pytest** - Testing framework with async support

### Development Notes
- Database tables are auto-created on startup via `Base.metadata.create_all()`
- The application serves API documentation at `/docs` (Swagger) and `/redoc`
- CORS is configured to allow all origins in development
- Custom exception handling converts `BaseError` exceptions to JSON responses