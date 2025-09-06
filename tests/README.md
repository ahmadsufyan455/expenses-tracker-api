# Integration Tests

This directory contains comprehensive integration tests for all API endpoints in the Expenses Tracker application.

## Test Structure

```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Pytest configuration and fixtures
├── test_auth_integration.py        # Authentication endpoint tests
├── test_budgets_integration.py     # Budget endpoint tests  
├── test_categories_integration.py  # Category endpoint tests
├── test_transactions_integration.py # Transaction endpoint tests
├── test_user_integration.py        # User profile endpoint tests
└── README.md                       # This file
```

## Test Coverage

### Authentication Tests (`test_auth_integration.py`)
- ✅ User registration (success, duplicate email, validation errors)
- ✅ User login (success, invalid credentials, validation errors)
- ✅ Error handling for missing fields and invalid data

### Category Tests (`test_categories_integration.py`)
- ✅ Create categories (success, duplicates, validation)
- ✅ Get categories (empty list, with data)
- ✅ Update categories (success, not found, partial updates)
- ✅ Delete categories (success, not found)
- ✅ Authorization checks for all operations

### Budget Tests (`test_budgets_integration.py`)
- ✅ Create budgets (success, duplicates, invalid data)
- ✅ Get budgets (empty list, with data)
- ✅ Update budgets (success, not found, month changes)
- ✅ Delete budgets (success, not found)
- ✅ Month format validation
- ✅ Authorization checks for all operations

### Transaction Tests (`test_transactions_integration.py`)
- ✅ Create income transactions (no budget required)
- ✅ Create expense transactions (budget validation)
- ✅ Budget enforcement (required budget, amount limits)
- ✅ Get transactions (empty list, with data)
- ✅ Update transactions (success, budget validation)
- ✅ Delete transactions (success, not found)
- ✅ Authorization checks for all operations

### User Profile Tests (`test_user_integration.py`)
- ✅ Get user profile (success, unauthorized)
- ✅ Update user profile (success, partial updates, validation)
- ✅ Change password (success, wrong current password, validation)
- ✅ Delete user account (success, cleanup verification)
- ✅ Authorization checks for all operations

## Key Features Tested

### 🔐 Authentication & Authorization
- JWT token-based authentication
- Proper authorization for all protected endpoints
- User isolation (users can only access their own data)

### 💰 Budget Management
- Budget creation with month validation
- Expense transaction budget enforcement
- Budget update and deletion
- Duplicate prevention per category/month

### 📊 Transaction Processing
- Income vs Expense transaction handling
- Budget deduction for expense transactions
- Transaction CRUD operations with proper validation

### 🏷️ Category Management
- Category CRUD operations
- User-specific category isolation
- Duplicate name prevention per user

### 👤 User Management
- Profile management operations
- Password change functionality
- Account deletion with proper cleanup

## Test Fixtures

### Core Fixtures (defined in `conftest.py`)

- **`client`** - FastAPI test client with database override
- **`db_session`** - Fresh database session for each test
- **`authenticated_user`** - Registered user with valid JWT token
- **`sample_*_data`** - Sample data for creating test entities

### Composite Fixtures

- **`created_category`** - Pre-created category for tests
- **`created_budget`** - Pre-created budget for tests
- **`created_transaction`** - Pre-created transaction for tests

## Running Tests

### Prerequisites

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure you're in the project root directory

### Run All Tests
```bash
python run_tests.py all
```

### Run Specific Test Suites
```bash
# Authentication tests
python run_tests.py auth

# Budget tests  
python run_tests.py budgets

# Category tests
python run_tests.py categories

# Transaction tests
python run_tests.py transactions

# User profile tests
python run_tests.py user
```

### Run with Coverage Report
```bash
python run_tests.py coverage
```

### Run with Verbose Output
```bash
python run_tests.py verbose
```

### Using pytest directly
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_auth_integration.py

# Run specific test class
pytest tests/test_auth_integration.py::TestAuthEndpoints

# Run specific test method
pytest tests/test_auth_integration.py::TestAuthEndpoints::test_register_success

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Test Database

- Tests use SQLite in-memory database (`test.db`)
- Fresh database created for each test function
- Automatic cleanup after each test
- No interference with development/production databases

## Test Patterns

### 1. Happy Path Testing
Each endpoint tests the successful case first:
```python
def test_create_category_success(self, client, authenticated_user, sample_category_data):
    response = client.post("/api/v1/categories/", json=sample_category_data, headers=authenticated_user["headers"])
    assert response.status_code == 201
    # ... additional assertions
```

### 2. Error Case Testing
Comprehensive error scenario coverage:
```python
def test_create_category_unauthorized(self, client, sample_category_data):
    response = client.post("/api/v1/categories/", json=sample_category_data)
    assert response.status_code == 401
```

### 3. Validation Testing
Input validation and business rule enforcement:
```python
def test_create_expense_transaction_no_budget(self, client, authenticated_user, created_category):
    # Test business rule: expense transactions require budgets
    assert response.status_code == 400
    assert data["message"] == BudgetMessages.REQUIRED_FOR_EXPENSE.value
```

### 4. Data Integrity Testing
Verification of proper data handling:
```python
def test_delete_category_success(self, client, authenticated_user, created_category):
    # Delete operation
    response = client.delete(f"/api/v1/categories/{created_category['id']}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get("/api/v1/categories/")
    assert len(get_response.json()["data"]) == 0
```

## Best Practices Implemented

1. **Isolation** - Each test is independent and can run in any order
2. **Cleanup** - Database is reset between tests
3. **Realistic Data** - Tests use realistic sample data
4. **Comprehensive Coverage** - Both success and failure paths tested
5. **Clear Assertions** - Tests verify both HTTP status and response content
6. **Proper Authentication** - Tests verify authorization requirements
7. **Business Logic** - Tests verify business rules (e.g., budget enforcement)

## Extending Tests

When adding new endpoints or modifying existing ones:

1. **Add test methods** following the naming convention `test_<operation>_<scenario>`
2. **Use existing fixtures** when possible to maintain consistency
3. **Test both success and error cases** for comprehensive coverage
4. **Verify business rules** specific to your domain logic
5. **Update this README** with any new test categories or patterns

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure you're running tests from the project root
2. **Database Errors** - Check that SQLAlchemy models are properly configured
3. **Authentication Errors** - Verify JWT token generation in fixtures
4. **Fixture Errors** - Check dependency chain in `conftest.py`

### Debug Mode

Run tests with verbose output to see detailed information:
```bash
python run_tests.py verbose
```

Or with pytest directly:
```bash
pytest tests/ -v -s --tb=long
```
