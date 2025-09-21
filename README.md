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
- **Flexible Date Range Budgets** - Create budgets for any custom date range (days, weeks, months, or cross-month periods)
- **Overlap Prevention** - Smart validation prevents overlapping budgets for the same category
- **Budget Enforcement** - Prevents expense recording without corresponding budget
- **Budget Predictions** - Calculate daily spending allowances based on remaining budget
- **Multiple Prediction Types** - Daily, weekdays-only, weekends-only, or custom day counts
- **Real-time Calculations** - Dynamic budget tracking with remaining balance
- **Financial Discipline** - Encourages proactive budget planning
- **Raw SQL Optimization** - High-performance overlap detection using native SQL queries

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
GET    /api/v1/budgets/            # Get user budgets with predictions
POST   /api/v1/budgets/            # Create new date range budget with overlap prevention
PUT    /api/v1/budgets/{id}        # Update budget (validates against overlaps)
DELETE /api/v1/budgets/{id}        # Delete budget

# Budget Schema (New Date Range Format)
{
  "category_id": 1,
  "amount": 50000,
  "start_date": "2025-09-27",      # Start date of budget period
  "end_date": "2025-10-27",        # End date of budget period
  "prediction_enabled": true,
  "prediction_type": "daily",       # daily|weekdays|weekends|custom
  "prediction_days_count": 15       # Required if prediction_type = "custom"
}
```

### Dashboard
```
GET    /api/v1/dashboard/          # Get comprehensive dashboard data
       ?month=YYYY-MM             # Optional: filter by specific month
       &transaction_limit=5       # Limit recent transactions (1-50)
       &expense_limit=3           # Limit top expense categories (1-10)
       &budget_limit=3            # Limit budget overview items (1-10)
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
│   │       ├── dashboard.py  # Dashboard analytics
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
│   │   ├── dashboard_repository.py
│   │   ├── transaction_repository.py
│   │   └── user_repository.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py          # Authentication schemas
│   │   ├── budget.py        # Budget schemas
│   │   ├── category.py      # Category schemas
│   │   ├── dashboard.py     # Dashboard schemas
│   │   ├── transaction.py   # Transaction schemas
│   │   └── user.py          # User schemas
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py  # Authentication service
│   │   ├── budget_service.py # Budget service
│   │   ├── category_service.py # Category service
│   │   ├── dashboard_service.py # Dashboard service
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

### 3. Set Date Range Budget with Prediction
```bash
# Traditional monthly budget
POST /api/v1/budgets/
{
  "category_id": 1,
  "amount": 50000,
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "prediction_enabled": true,
  "prediction_type": "daily"
}

# Cross-month budget (e.g., 27 Sep to 27 Oct)
POST /api/v1/budgets/
{
  "category_id": 2,
  "amount": 120000,
  "start_date": "2025-09-27",
  "end_date": "2025-10-27",
  "prediction_enabled": true,
  "prediction_type": "weekdays"
}

# Short-term budget (one week)
POST /api/v1/budgets/
{
  "category_id": 3,
  "amount": 30000,
  "start_date": "2025-10-01",
  "end_date": "2025-10-07"
}
```

## 🎯 Date Range Budget Feature

### Flexible Budget Periods
Create budgets for any time period that suits your needs:

- **Traditional Monthly**: `2025-01-01` to `2025-01-31`
- **Cross-Month Periods**: `2025-09-27` to `2025-10-27` (your specific use case!)
- **Short-Term**: `2025-10-01` to `2025-10-07` (one week)
- **Custom Periods**: Any start and end date combination

### Overlap Prevention Examples

```bash
# ✅ ALLOWED: Sequential budgets for same category
Budget 1: Food (2025-09-01 to 2025-09-26)
Budget 2: Food (2025-09-27 to 2025-10-27)  # Starts after Budget 1 ends
Budget 3: Food (2025-10-28 to 2025-11-27)  # Continues after Budget 2

# ❌ BLOCKED: Overlapping budgets for same category
Budget 1: Food (2025-09-27 to 2025-10-27)
Budget 2: Food (2025-10-15 to 2025-11-15)  # ERROR: Overlaps with Budget 1

# ✅ ALLOWED: Different categories can overlap
Food Budget:   2025-09-27 to 2025-10-27
Travel Budget: 2025-09-27 to 2025-10-27  # Different category = OK
```

### Transaction Validation
- Transactions are validated against the budget that covers their date
- A transaction on `2025-10-15` will use the budget with `start_date <= 2025-10-15 <= end_date`
- If no budget covers the transaction date, the expense will be rejected

### Prediction System
The prediction system automatically adapts to your custom date ranges:
- Calculates remaining days based on your budget period (not calendar months)
- Supports all prediction types (daily, weekdays, weekends, custom) within your date range
- Works perfectly with cross-month budgets

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
- **Expense transactions** require an active budget that covers the transaction date
- **Income transactions** can be created without budgets
- **Date Range Validation** - Transactions are validated against budget periods, not just months
- **Overlap Prevention** - System prevents creating overlapping budgets for the same category
- Users must plan budgets before spending (promotes financial discipline)

### Data Integrity
- **No overlapping budgets** per category (enforced by raw SQL validation)
- **Flexible date ranges** - budgets can span any period (days, weeks, months, cross-month)
- **Adjacent budgets allowed** - sequential budgets with no gaps are permitted
- **Multi-category support** - different categories can have overlapping date ranges
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
