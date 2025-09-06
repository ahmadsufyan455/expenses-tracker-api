from enum import Enum


class TransactionMessages(Enum):
    CREATED_SUCCESS = "Transaction created successfully"
    UPDATED_SUCCESS = "Transaction updated successfully"
    DELETED_SUCCESS = "Transaction deleted successfully"
    RETRIEVED_SUCCESS = "Transactions retrieved successfully"
    NOT_FOUND = "Transaction not found"
    INVALID_BUDGET_NOT_FOUND = "You must create a budget for this category in the current month before creating an expense transaction"
    EXCEEDED_LIMIT = "This transaction exceeds your remaining budget for this category this month. Please adjust your budget or reduce the amount."


class BudgetMessages(Enum):
    CREATED_SUCCESS = "Budget created successfully"
    UPDATED_SUCCESS = "Budget updated successfully"
    DELETED_SUCCESS = "Budget deleted successfully"
    RETRIEVED_SUCCESS = "Budgets fetched successfully"
    NOT_FOUND = "Budget not found"
    ALREADY_EXISTS = "Budget already exists for this category and month"
    REQUIRED_FOR_EXPENSE = "You must create a budget for this category in the current month before creating an expense transaction"
    EXCEEDED_LIMIT = "This transaction exceeds your remaining budget for this category this month. Please adjust your budget or reduce the amount."
    INVALID_MONTH_FORMAT = "Invalid month format. Use YYYY-MM format (e.g., '2025-09')"


class ValidationMessages(Enum):
    INVALID_AMOUNT = "Amount must be greater than zero"
    INVALID_DATE_FORMAT = "Invalid date format. Use YYYY-MM-DD"
    PASSWORD_TOO_SHORT = "Password must be at least 8 characters long"
    INVALID_EMAIL = "Invalid email format"


class AuthMessages(Enum):
    LOGIN_SUCCESS = "Login successful"
    REGISTER_SUCCESS = "Register successful"
    USER_NOT_FOUND = "User not found"
    INVALID_PASSWORD = "Invalid password"
    ALREADY_EXISTS = "User already exists"
    TOKEN_EXPIRED = "Token has expired"
    UNAUTHORIZED = "Unauthorized access"


class UserMessages(Enum):
    RETRIEVED_SUCCESS = "Profile retrieved successfully"
    UPDATED_SUCCESS = "Profile updated successfully"
    PASSWORD_CHANGED_SUCCESS = "Password changed successfully"
    INVALID_CURRENT_PASSWORD = "Invalid current password"


class CategoryMessages(Enum):
    CREATED_SUCCESS = "Category created successfully"
    UPDATED_SUCCESS = "Category updated successfully"
    DELETED_SUCCESS = "Category deleted successfully"
    RETRIEVED_SUCCESS = "Categories retrieved successfully"
    NOT_FOUND = "Category not found"
    ALREADY_EXISTS = "Category already exists"


class ErrorMessages(Enum):
    INTERNAL_SERVER_ERROR = "An internal server error occurred"
    NOT_FOUND = "Resource not found"
    FORBIDDEN = "Access forbidden"
    BAD_REQUEST = "Bad request"
