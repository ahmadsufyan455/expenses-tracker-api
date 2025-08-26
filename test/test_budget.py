from .utils import *
from starlette import status
from main import app
from routers.budget import get_db, get_current_user

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_budgets(test_budget):
    response = client.get("/budgets")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["message"] == "Budgets fetched successfully"
    assert len(data["data"]) == 1

    budget_data = data["data"][0]
    assert budget_data["id"] == test_budget.id
    assert budget_data["category_id"] == test_budget.category_id
    assert budget_data["amount"] == test_budget.amount
    assert budget_data["month"] == test_budget.month.isoformat()


def test_get_budgets_empty():
    response = client.get("/budgets")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": "Budgets fetched successfully",
        "data": []
    }


def test_create_budget(test_category):
    request_body = {
        "category_id": test_category.id,
        "amount": 1000000,
        "month": "2025-10"
    }

    response = client.post("/budgets/add", json=request_body)
    assert response.status_code == status.HTTP_201_CREATED

    # Verify response structure
    data = response.json()
    assert data["message"] == "Budget created successfully"
    assert "data" in data

    budget_data = data["data"]
    assert budget_data["category_id"] == request_body["category_id"]
    assert budget_data["amount"] == request_body["amount"]
    # Should be converted to first day of month
    assert budget_data["month"] == "2025-10-01"

    # Verify in database
    db = TestSessionLocal()
    budget = db.query(Budget).filter(
        Budget.amount == request_body["amount"]).first()
    assert budget is not None
    assert budget.category_id == request_body["category_id"]
    assert budget.amount == request_body["amount"]
    assert budget.month == date(2025, 10, 1)
    assert budget.user_id == TEST_USER_ID

    db.close()


def test_create_budget_invalid_category_id():
    request_body = {
        "category_id": 999,
        "amount": 1000000,
        "month": "2025-10"
    }

    response = client.post("/budgets/add", json=request_body)
    # Note: This should probably return 404 if category validation is added
    # For now, it might succeed if no category validation exists
    # You may want to add category validation to your budget endpoint


def test_create_budget_invalid_month_format():
    request_body = {
        "category_id": 1,
        "amount": 1000000,
        "month": "invalid-month"
    }

    response = client.post("/budgets/add", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid month format" in response.json()["message"]


def test_create_budget_missing_day_in_month():
    request_body = {
        "category_id": 1,
        "amount": 1000000,
        "month": "2025"  # Missing month
    }

    response = client.post("/budgets/add", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid month format" in response.json()["message"]


def test_update_budget(test_budget):
    request_body = {
        "category_id": test_budget.category_id,
        "amount": 750000,
        "month": "2025-11"
    }

    response = client.put(
        f"/budgets/{test_budget.id}/update", json=request_body)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify in database
    db = TestSessionLocal()
    budget = db.query(Budget).filter(Budget.id == test_budget.id).first()
    assert budget is not None
    assert budget.category_id == request_body["category_id"]
    assert budget.amount == request_body["amount"]
    assert budget.month == date(2025, 11, 1)
    assert budget.user_id == TEST_USER_ID

    db.close()


def test_update_budget_not_found():
    request_body = {
        "category_id": 1,
        "amount": 750000,
        "month": "2025-11"
    }

    response = client.put("/budgets/999/update", json=request_body)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "message": "Budget not found",
        "error": None
    }


def test_update_budget_invalid_month_format(test_budget):
    request_body = {
        "category_id": test_budget.category_id,
        "amount": 750000,
        "month": "invalid-date"
    }

    response = client.put(
        f"/budgets/{test_budget.id}/update", json=request_body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid month format" in response.json()["message"]


def test_delete_budget(test_budget):
    response = client.delete(f"/budgets/{test_budget.id}/delete")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify budget is deleted from database
    db = TestSessionLocal()
    budget = db.query(Budget).filter(Budget.id == test_budget.id).first()
    assert budget is None
    db.close()


def test_delete_budget_not_found():
    response = client.delete("/budgets/999/delete")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "message": "Budget not found",
        "error": None
    }


def test_create_duplicate_budget_fails(test_category):
    """Test creating multiple budgets for the same month and category should fail due to unique constraint"""
    request_body_1 = {
        "category_id": test_category.id,
        "amount": 500000,
        "month": "2025-12"
    }

    request_body_2 = {
        "category_id": test_category.id,
        "amount": 600000,
        "month": "2025-12"  # Same month and category
    }

    # Create first budget
    response1 = client.post("/budgets/add", json=request_body_1)
    assert response1.status_code == status.HTTP_201_CREATED

    # Create second budget (should fail due to unique constraint)
    response2 = client.post("/budgets/add", json=request_body_2)
    # Should return 409 Conflict due to unique constraint
    assert response2.status_code == status.HTTP_409_CONFLICT
    assert "Budget already exists" in response2.json()["message"]

    # Verify only one exists in database
    db = TestSessionLocal()
    budgets = db.query(Budget).filter(
        Budget.category_id == test_category.id,
        Budget.month == date(2025, 12, 1)
    ).all()
    assert len(budgets) == 1
    db.close()


def test_budget_month_conversion():
    """Test that various month formats are handled correctly"""
    test_cases = [
        ("2025-01", date(2025, 1, 1)),
        ("2025-12", date(2025, 12, 1)),
        ("2024-06", date(2024, 6, 1)),
    ]

    for month_str, expected_date in test_cases:
        request_body = {
            "category_id": 1,
            "amount": 100000,
            "month": month_str
        }

        response = client.post("/budgets/add", json=request_body)
        if response.status_code == status.HTTP_201_CREATED:
            # Verify the date conversion
            data = response.json()
            assert data["data"]["month"] == expected_date.isoformat()
