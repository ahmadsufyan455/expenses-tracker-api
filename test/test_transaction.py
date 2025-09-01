from .utils import *
from starlette import status
from main import app
from routers.transaction import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_transactions(test_transaction):
    response = client.get("/transactions")
    assert response.status_code == status.HTTP_200_OK
    print(f"response.json(): {response.json()}")
    assert response.json() == {
        "message": "Transactions retrieved successfully",
        "data": [
            {
                "id": str(test_transaction.id),
                "category_id": test_transaction.category_id,
                "amount": test_transaction.amount,
                "type": test_transaction.type.value,
                "payment_method": test_transaction.payment_method.value,
                "description": test_transaction.description,
                "created_at": test_transaction.created_at.isoformat()
            }
        ]
    }


def test_create_transaction(test_transaction):
    request_body = {
        "amount": 10000,
        "type": "income",
        "payment_method": "cash",
        "category_id": 1,
        "description": "Test Transaction"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestSessionLocal()

    transaction = db.query(Transaction).filter(
        Transaction.description == "Test Transaction"
    ).first()

    assert transaction is not None
    assert transaction.amount == request_body["amount"]
    assert transaction.type.value == 'income'
    assert transaction.payment_method.value == "cash"
    assert transaction.category_id == request_body["category_id"]
    assert transaction.description == request_body["description"]
    assert transaction.user_id == TEST_USER_ID

    db.close()


def test_create_transaction_invalid_category_id(test_transaction):
    request_body = {
        "amount": 10000,
        "type": "expense",
        "payment_method": "cash",
        "category_id": 999,
        "description": "Test Transaction"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "message": "Category not found",
        "error": None
    }


def test_create_expense_transaction_with_budget(test_budget):
    """Test creating expense transaction when budget exists for current month"""
    request_body = {
        "amount": 100000,
        "type": "expense",
        "payment_method": "cash",
        "category_id": test_budget.category_id,
        "description": "Test Expense with Budget"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED

    # Verify transaction was created
    db = TestSessionLocal()
    transaction = db.query(Transaction).filter(
        Transaction.description == "Test Expense with Budget"
    ).first()

    assert transaction is not None
    assert transaction.amount == request_body["amount"]
    assert transaction.type.value == "expense"
    assert transaction.category_id == test_budget.category_id
    assert transaction.user_id == TEST_USER_ID

    db.close()


def test_create_expense_transaction_without_budget(test_category):
    """Test creating expense transaction when no budget exists for current month"""
    request_body = {
        "amount": 100000,
        "type": "expense",
        "payment_method": "cash",
        "category_id": test_category.id,
        "description": "Test Expense without Budget"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_data = response.json()
    assert "Please set a budget for" in response_data["message"]
    assert "category for" in response_data["message"]
    assert "before adding expenses" in response_data["message"]

    # Verify transaction was NOT created
    db = TestSessionLocal()
    transaction = db.query(Transaction).filter(
        Transaction.description == "Test Expense without Budget"
    ).first()
    assert transaction is None

    db.close()


def test_create_income_transaction_without_budget(test_category):
    """Test creating income transaction when no budget exists (should succeed)"""
    request_body = {
        "amount": 500000,
        "type": "income",
        "payment_method": "bank_transfer",
        "category_id": test_category.id,
        "description": "Test Income without Budget"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED

    # Verify transaction was created
    db = TestSessionLocal()
    transaction = db.query(Transaction).filter(
        Transaction.description == "Test Income without Budget"
    ).first()

    assert transaction is not None
    assert transaction.amount == request_body["amount"]
    assert transaction.type.value == "income"
    assert transaction.category_id == test_category.id
    assert transaction.user_id == TEST_USER_ID

    db.close()


def test_create_expense_transaction_with_old_budget(test_category):
    """Test creating expense transaction when budget exists but for different month"""
    # Create budget for previous month (August 2025)
    db = TestSessionLocal()
    old_budget = Budget(
        user_id=TEST_USER_ID,
        category_id=test_category.id,
        amount=300000,
        month=date(2025, 8, 1)  # August 2025, different from current month
    )
    db.add(old_budget)
    db.commit()

    request_body = {
        "amount": 50000,
        "type": "expense",
        "payment_method": "credit_card",
        "category_id": test_category.id,
        "description": "Test Expense with Old Budget"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_data = response.json()
    assert "Please set a budget for" in response_data["message"]
    assert "before adding expenses" in response_data["message"]

    # Verify transaction was NOT created
    transaction = db.query(Transaction).filter(
        Transaction.description == "Test Expense with Old Budget"
    ).first()
    assert transaction is None

    db.close()


def test_create_expense_transaction_budget_validation_message(test_category):
    """Test that budget validation error message contains correct category name and month"""
    request_body = {
        "amount": 75000,
        "type": "expense",
        "payment_method": "digital_wallet",
        "category_id": test_category.id,
        "description": "Test Budget Error Message"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response_data = response.json()
    error_message = response_data["message"]

    # Check that error message contains category name
    assert test_category.name in error_message
    # Check that error message contains current month/year
    current_month_year = datetime.now().strftime('%B %Y')
    assert current_month_year in error_message
    # Check full message structure
    expected_message = f"Please set a budget for {test_category.name} category for {current_month_year} before adding expenses"
    assert error_message == expected_message


def test_multiple_expense_transactions_with_same_budget(test_budget):
    """Test creating multiple expense transactions against the same budget"""
    # First transaction
    request_body_1 = {
        "amount": 100000,
        "type": "expense",
        "payment_method": "cash",
        "category_id": test_budget.category_id,
        "description": "First Expense Transaction"
    }

    response_1 = client.post("/transactions/add", json=request_body_1)
    assert response_1.status_code == status.HTTP_201_CREATED

    # Second transaction with same budget
    request_body_2 = {
        "amount": 150000,
        "type": "expense",
        "payment_method": "credit_card",
        "category_id": test_budget.category_id,
        "description": "Second Expense Transaction"
    }

    response_2 = client.post("/transactions/add", json=request_body_2)
    assert response_2.status_code == status.HTTP_201_CREATED

    # Verify both transactions were created
    db = TestSessionLocal()
    transactions = db.query(Transaction).filter(
        Transaction.category_id == test_budget.category_id,
        Transaction.type == TransactionType.EXPENSE
    ).all()

    # Should have at least 2 expense transactions for this category
    expense_transactions = [t for t in transactions if t.description in [
        "First Expense Transaction", "Second Expense Transaction"]]
    assert len(expense_transactions) == 2

    db.close()


def test_update_transaction(test_transaction):
    request_body = {
        "amount": 50000,
        "type": "income",
        "payment_method": "bank_transfer",
        "category_id": 1,
        "description": "Updated Test Transaction"
    }

    response = client.put(
        f"/transactions/{test_transaction.id}/update", json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestSessionLocal()
    transaction = db.query(Transaction).filter(
        Transaction.id == test_transaction.id).first()
    assert transaction.amount == request_body["amount"]
    assert transaction.type.value == 'income'
    assert transaction.payment_method.value == "bank_transfer"
    assert transaction.category_id == request_body["category_id"]
    assert transaction.description == request_body["description"]
    assert transaction.user_id == TEST_USER_ID

    db.close()


def test_update_transaction_not_found(test_transaction):
    request_body = {
        "amount": 50000,
        "type": "income",
        "payment_method": "bank_transfer",
        "category_id": 1,
        "description": "Updated Test Transaction"
    }

    response = client.put(
        f"/transactions/997f7e5c-23f0-44f4-b5ca-b0988838b19e/update", json=request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_transaction(test_transaction):
    response = client.delete(
        f"/transactions/{test_transaction.id}/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestSessionLocal()
    transaction = db.query(Transaction).filter(
        Transaction.id == test_transaction.id).first()
    assert transaction is None


def test_delete_transaction_not_found(test_transaction):
    response = client.delete(
        "/transactions/997f7e5c-23f0-44f4-b5ca-b0988838b19e/delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND
