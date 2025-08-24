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
        "type": "expense",
        "payment_method": "cash",
        "category_id": 1,
        "description": "Test Transaction"
    }

    response = client.post("/transactions/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestSessionLocal()
    # because we don't know the randon UUID
    # we need to get all transactions and get index 1
    # because index 0 is the test_transaction
    transaction = db.query(Transaction).all()

    assert transaction[1].amount == request_body["amount"]
    assert transaction[1].type.value == 'expense'
    assert transaction[1].payment_method.value == "cash"
    assert transaction[1].category_id == request_body["category_id"]
    assert transaction[1].description == request_body["description"]
    assert transaction[1].user_id == TEST_USER_ID

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
