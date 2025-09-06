# 💰 Personal Expense Tracker API

A comprehensive RESTful API for personal expense tracking built with FastAPI, featuring budget management, transaction categorization, and file attachments.

## 🚀 Features

### 👤 User Management
- **User Registration & Authentication** - Secure JWT-based authentication
- **Password Hashing** - Bcrypt encryption for user security
- **Protected Routes** - Bearer token authentication for all endpoints

### 📊 Category Management
- **Create Categories** - Organize expenses by custom categories
- **CRUD Operations** - Full create, read, update, delete functionality
- **User-specific Categories** - Each user manages their own categories

### 💸 Transaction Management
- **Income & Expense Tracking** - Record both income and expense transactions
- **Multiple Payment Methods** - Cash, Credit Card, Bank Transfer, Digital Wallet
- **Transaction History** - Complete transaction logging with timestamps
- **Budget Validation** - Enforces budget creation before expense recording
- **Integer-based IDs** - Simple and efficient transaction identification

### 📅 Budget Planning
- **Monthly Budgets** - Set spending limits by category and month
- **Budget Enforcement** - Prevents expense recording without corresponding budget
- **Financial Discipline** - Encourages proactive budget planning
- **Unique Constraints** - One budget per category per month

### 🔧 Architecture
- **Clean Architecture** - Separation of concerns with repositories, services, and API layers
- **Dependency Injection** - Proper dependency management with FastAPI's DI system
- **Enum-based Messages** - Centralized message management for consistency
- **Comprehensive Testing** - Full integration test coverage

## 🛠️ Technology Stack

- **Backend Framework:** FastAPI
- **Database:** PostgreSQL (Production) / SQLite (Testing)
- **ORM:** SQLAlchemy
- **Authentication:** JWT with PassLib
- **Testing:** Pytest
- **Database Migrations:** Alembic
- **Validation:** Pydantic

## 📋 API Endpoints

### Authentication
```
POST /api/v1/auth/register   # User registration
POST /api/v1/auth/login      # User login
```

### Users
```
GET    /api/v1/users/              # Get user profile
PUT    /api/v1/users/              # Update user profile
DELETE /api/v1/users/              # Delete user account
POST   /api/v1/users/change-password # Change password
```

### Categories
```
GET    /api/v1/categories/         # Get user categories
POST   /api/v1/categories/         # Create new category
PUT    /api/v1/categories/{id}     # Update category
DELETE /api/v1/categories/{id}     # Delete category
```

### Transactions
```
GET    /api/v1/transactions/       # Get user transactions
POST   /api/v1/transactions/       # Create new transaction (with budget validation)
PUT    /api/v1/transactions/{id}/update  # Update transaction
DELETE /api/v1/transactions/{id}/delete  # Delete transaction
```

### Budgets
```
GET    /api/v1/budgets/            # Get user budgets
POST   /api/v1/budgets/            # Create new budget
PUT    /api/v1/budgets/{id}        # Update budget
DELETE /api/v1/budgets/{id}        # Delete budget
```

## 🏗️ Project Structure

```
expenses-tracker/
├── app/                     # Main application package
│   ├── api/                 # API layer
│   │   └── v1/              # API version 1
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── budgets.py   # Budget management
│   │       ├── categories.py # Category management
│   │       ├── transactions.py # Transaction management
│   │       ├── user.py      # User profile management
│   │       └── router.py    # Main API router
│   ├── config/              # Configuration
│   │   ├── database.py      # Database connection
│   │   └── settings.py      # Application settings
│   ├── constants/           # Application constants
│   │   └── messages.py      # Response messages (enum-based)
│   ├── core/                # Core utilities
│   │   ├── dependencies.py  # Dependency injection
│   │   ├── exceptions.py    # Custom exceptions
│   │   ├── responses.py     # Standardized API responses
│   │   └── security.py      # JWT security utilities
│   ├── models/              # SQLAlchemy models
│   │   ├── base.py          # Base model
│   │   ├── budget.py        # Budget model
│   │   ├── category.py      # Category model
│   │   ├── transaction.py   # Transaction model
│   │   └── user.py          # User model
│   ├── repositories/        # Data access layer
│   │   ├── base.py          # Base repository
│   │   ├── budget_repository.py
│   │   ├── category_repository.py
│   │   ├── transaction_repository.py
│   │   └── user_repository.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py          # Authentication schemas
│   │   ├── budget.py        # Budget schemas
│   │   ├── category.py      # Category schemas
│   │   ├── transaction.py   # Transaction schemas
│   │   └── user.py          # User schemas
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py  # Authentication service
│   │   ├── budget_service.py # Budget service
│   │   ├── category_service.py # Category service
│   │   ├── transaction_service.py # Transaction service
│   │   └── user_service.py  # User service
│   ├── utils/               # Utilities
│   │   └── validation.py    # Validation helpers
│   └── main.py              # FastAPI application entry point
├── tests/                   # Integration test suite
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_auth_integration.py      # Authentication integration tests
│   ├── test_budgets_integration.py   # Budget integration tests
│   ├── test_categories_integration.py # Category integration tests
│   ├── test_transactions_integration.py # Transaction integration tests
│   ├── test_user_integration.py      # User integration tests
│   └── README.md            # Test documentation
├── run_tests.py             # Test runner script
├── pytest.ini              # Pytest configuration
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL (for production)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahmadsufyan455/expenses-tracker-api.git
   cd expenses-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   DATABASE_URL=postgresql://username:password@localhost/expenses_db
   ```

5. **Database Setup**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once the application is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🧪 Testing

Run the comprehensive integration test suite:

```bash
# Run all tests
python run_tests.py all

# Run specific test suites
python run_tests.py auth        # Authentication tests
python run_tests.py budgets     # Budget tests
python run_tests.py categories  # Category tests
python run_tests.py transactions # Transaction tests
python run_tests.py user        # User profile tests

# Run with coverage report
python run_tests.py coverage

# Run with verbose output
python run_tests.py verbose

# Using pytest directly
pytest tests/                   # Run all tests
pytest tests/test_auth_integration.py  # Run specific test file
pytest -v                      # Verbose output
pytest --cov=app --cov-report=html    # Coverage with HTML report
```

### Integration Test Coverage
- ✅ **Authentication** (10 tests) - Registration, login, JWT validation, error handling
- ✅ **Categories** (13 tests) - CRUD operations, authorization, duplicate prevention
- ✅ **Budgets** (14 tests) - CRUD operations, month validation, constraint enforcement
- ✅ **Transactions** (15 tests) - CRUD operations, budget enforcement, business logic validation
- ✅ **User Profile** (13 tests) - Profile management, password changes, account deletion
- ✅ **Edge Cases** - Unauthorized access, validation errors, data integrity

### Test Features
- **Database Isolation** - Each test uses a fresh in-memory SQLite database
- **Authentication Testing** - JWT token-based authentication for protected endpoints
- **Business Logic Validation** - Budget enforcement, transaction validation
- **Error Scenario Coverage** - Comprehensive testing of error conditions
- **Real API Testing** - Full HTTP request/response testing with FastAPI TestClient

## 🔄 Usage Flow

### 1. Initial Setup
```bash
# Register user
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securePassword123"
}

# Login to get token
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### 2. Create Categories
```bash
POST /api/v1/categories/
{
  "name": "Food"
}
```

### 3. Set Monthly Budget
```bash
POST /api/v1/budgets/
{
  "category_id": 1,
  "amount": 50000,
  "month": "2025-01"
}
```

### 4. Record Transactions
```bash
# This will succeed (budget exists)
POST /api/v1/transactions/
{
  "category_id": 1,
  "amount": 2500,
  "type": "expense",
  "payment_method": "cash",
  "description": "Grocery shopping"
}
```

## 🎯 Key Business Logic

### Budget Enforcement
- **Expense transactions** require an active budget for the current month
- **Income transactions** can be created without budgets
- Users must plan budgets before spending (promotes financial discipline)

### Data Integrity
- One budget per category per month (unique constraint)
- Integer-based IDs for simplicity and efficiency
- Cascade deletes for data consistency
- Comprehensive validation at all levels

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Ahmad Sufyan**
- LinkedIn: [https://www.linkedin.com/in/ahmadsufyan455/](https://www.linkedin.com/in/ahmadsufyan455/)
- Email: ahmadsufyan514@gmail.com

---

⭐ Star this repository if you found it helpful!
