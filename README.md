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
- **UUID-based IDs** - Scalable transaction identification

### 📅 Budget Planning
- **Monthly Budgets** - Set spending limits by category and month
- **Budget Enforcement** - Prevents expense recording without corresponding budget
- **Financial Discipline** - Encourages proactive budget planning
- **Unique Constraints** - One budget per category per month

### 📎 File Attachments
- **Receipt Storage** - Upload and manage transaction receipts
- **Multiple File Types** - Support for images, PDFs, and documents
- **Transaction Linking** - Attach multiple files to any transaction
- **File Management** - Complete CRUD operations for attachments

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
POST /auth/register          # User registration
POST /auth/login            # User login
```

### Categories
```
GET    /categories          # Get user categories
POST   /categories/add      # Create new category
PUT    /categories/{id}/update    # Update category
DELETE /categories/{id}/delete    # Delete category
```

### Transactions
```
GET    /transactions        # Get user transactions
POST   /transactions/add    # Create new transaction (with budget validation)
PUT    /transactions/{id}/update  # Update transaction
DELETE /transactions/{id}/delete  # Delete transaction
```

### Budgets
```
GET    /budgets            # Get user budgets
POST   /budgets/add        # Create new budget
PUT    /budgets/{id}/update     # Update budget
DELETE /budgets/{id}/delete     # Delete budget
```

### Attachments
```
GET    /attachments/{transaction_id}/     # Get transaction attachments
POST   /attachments/{transaction_id}/add  # Upload attachment
DELETE /attachments/{id}/delete           # Delete attachment
```

## 🏗️ Project Structure

```
expenses-tracker/
├── alembic/                 # Database migrations
├── core/                    # Core utilities
│   ├── base_response.py     # Standardized API responses
│   └── validation.py        # User validation utilities
├── db/                      # Database configuration
│   ├── database.py          # Database connection
│   └── models.py            # SQLAlchemy models
├── routers/                 # API route handlers
│   ├── auth.py              # Authentication endpoints
│   ├── budget.py            # Budget management
│   ├── category.py          # Category management
│   ├── transaction.py       # Transaction management
│   └── attachment.py        # File attachment handling
├── test/                    # Test suite
│   ├── test_auth.py         # Authentication tests
│   ├── test_budget.py       # Budget tests
│   ├── test_category.py     # Category tests
│   ├── test_transaction.py  # Transaction tests
│   ├── test_attachment.py   # Attachment tests
│   └── utils.py             # Test utilities and fixtures
├── main.py                  # FastAPI application entry point
├── alembic.ini             # Alembic configuration
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
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

Once the application is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest test/test_transaction.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=routers
```

### Test Coverage
- ✅ User authentication and authorization
- ✅ Category CRUD operations
- ✅ Budget management with validation
- ✅ Transaction creation with budget enforcement
- ✅ File attachment handling
- ✅ Error handling and edge cases

## 🔄 Usage Flow

### 1. Initial Setup
```bash
# Register user
POST /auth/register
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securePassword123"
}

# Login to get token
POST /auth/login
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

### 2. Create Categories
```bash
POST /categories/add
{
  "name": "Food"
}
```

### 3. Set Monthly Budget
```bash
POST /budgets/add
{
  "category_id": 1,
  "amount": 500000,
  "month": "2024-01"
}
```

### 4. Record Transactions
```bash
# This will succeed (budget exists)
POST /transactions/add
{
  "category_id": 1,
  "amount": 75000,
  "type": "expense",
  "payment_method": "credit_card",
  "description": "Grocery shopping"
}
```

### 5. Upload Receipt
```bash
POST /attachments/{transaction_id}/add
# Upload file as multipart/form-data
```

## 🎯 Key Business Logic

### Budget Enforcement
- **Expense transactions** require an active budget for the current month
- **Income transactions** can be created without budgets
- Users must plan budgets before spending (promotes financial discipline)

### Data Integrity
- One budget per category per month (unique constraint)
- UUID-based transaction IDs for scalability
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
