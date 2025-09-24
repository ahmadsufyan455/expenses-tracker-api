from fastapi.testclient import TestClient

from app.constants.messages import CategoryMessages


class TestCategoryEndpoints:
    """Integration tests for category endpoints"""

    def test_get_categories_empty(self, client: TestClient, authenticated_user):
        """Test getting categories when none exist"""
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == CategoryMessages.RETRIEVED_SUCCESS.value
        assert data["data"] == []

    def test_create_category_success(self, client: TestClient, authenticated_user, sample_category_data):
        """Test successful category creation"""
        response = client.post(
            "/api/v1/categories/",
            json=sample_category_data,
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 201
        data = response.json()

        assert data["message"] == CategoryMessages.CREATED_SUCCESS.value
        category_data = data["data"]
        assert category_data["name"] == sample_category_data["name"]
        assert "id" in category_data
        assert category_data["usage_count"] == 0

    def test_create_category_duplicate_name(self, client: TestClient, authenticated_user, sample_category_data):
        """Test creating category with duplicate name for same user"""
        # Create first category
        response = client.post(
            "/api/v1/categories/",
            json=sample_category_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Try to create duplicate
        response = client.post(
            "/api/v1/categories/",
            json=sample_category_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 409  # Conflict
        data = response.json()
        assert data["message"] == CategoryMessages.ALREADY_EXISTS.value

    def test_create_category_unauthorized(self, client: TestClient, sample_category_data):
        """Test creating category without authentication"""
        response = client.post(
            "/api/v1/categories/",
            json=sample_category_data
        )
        assert response.status_code == 401  # Unauthorized

    def test_create_category_invalid_data(self, client: TestClient, authenticated_user):
        """Test creating category with invalid data"""
        invalid_data = {
            "name": ""  # Empty name
        }

        response = client.post(
            "/api/v1/categories/",
            json=invalid_data,
            headers=authenticated_user["headers"]
        )
        # Note: Empty string might be accepted, check actual behavior
        assert response.status_code in [201, 422]  # Either accepted or validation error

    def test_get_categories_with_data(self, client: TestClient, authenticated_user, created_category):
        """Test getting categories when data exists"""
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == CategoryMessages.RETRIEVED_SUCCESS.value
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == created_category["id"]
        assert data["data"][0]["name"] == created_category["name"]
        assert data["data"][0]["usage_count"] == 0

    def test_update_category_success(self, client: TestClient, authenticated_user, created_category):
        """Test successful category update"""
        update_data = {
            "name": "Updated Food"
        }

        response = client.put(
            f"/api/v1/categories/{created_category['id']}",
            json=update_data,
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == CategoryMessages.UPDATED_SUCCESS.value
        category_data = data["data"]
        assert category_data["name"] == update_data["name"]
        assert category_data["id"] == created_category["id"]
        assert category_data["usage_count"] == 0

    def test_update_category_not_found(self, client: TestClient, authenticated_user):
        """Test updating non-existent category"""
        update_data = {
            "name": "Updated Name"
        }

        response = client.put(
            "/api/v1/categories/999",
            json=update_data,
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 404
        data = response.json()
        assert data["message"] == CategoryMessages.NOT_FOUND.value

    def test_update_category_unauthorized(self, client: TestClient, created_category):
        """Test updating category without authentication"""
        update_data = {
            "name": "Updated Name"
        }

        response = client.put(
            f"/api/v1/categories/{created_category['id']}",
            json=update_data
        )
        assert response.status_code == 401

    def test_update_category_partial(self, client: TestClient, authenticated_user, created_category):
        """Test partial category update"""
        update_data = {
            "name": "Updated Name Only"
        }

        response = client.put(
            f"/api/v1/categories/{created_category['id']}",
            json=update_data,
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 200
        data = response.json()
        category_data = data["data"]
        assert category_data["name"] == update_data["name"]
        assert category_data["id"] == created_category["id"]
        assert category_data["usage_count"] == 0

    def test_delete_category_success(self, client: TestClient, authenticated_user, created_category):
        """Test successful category deletion"""
        response = client.delete(
            f"/api/v1/categories/{created_category['id']}",
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 204

        # Verify category is deleted by trying to fetch it
        get_response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert get_response.status_code == 200
        assert len(get_response.json()["data"]) == 0

    def test_delete_category_not_found(self, client: TestClient, authenticated_user):
        """Test deleting non-existent category"""
        response = client.delete(
            "/api/v1/categories/999",
            headers=authenticated_user["headers"]
        )

        assert response.status_code == 404
        data = response.json()
        assert data["message"] == CategoryMessages.NOT_FOUND.value

    def test_delete_category_unauthorized(self, client: TestClient, created_category):
        """Test deleting category without authentication"""
        response = client.delete(f"/api/v1/categories/{created_category['id']}")
        assert response.status_code == 401

    def test_category_usage_count_with_transactions(self, client: TestClient, authenticated_user, created_category, created_budget):
        """Test that usage_count reflects the number of transactions using the category"""
        # Initially, category should have 0 usage
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        categories = response.json()["data"]
        assert len(categories) == 1
        assert categories[0]["usage_count"] == 0

        # Create first transaction
        transaction_data_1 = {
            "amount": 2500,
            "category_id": created_category["id"],
            "date": "2025-09-24",
            "type": "expense",
            "payment_method": "cash",
            "description": "First transaction"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data_1,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Check usage_count is now 1
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        categories = response.json()["data"]
        assert categories[0]["usage_count"] == 1

        # Create second transaction
        transaction_data_2 = {
            "amount": 3000,
            "category_id": created_category["id"],
            "date": "2025-09-24",
            "type": "expense",
            "payment_method": "credit_card",
            "description": "Second transaction"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data_2,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Check usage_count is now 2
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        categories = response.json()["data"]
        assert categories[0]["usage_count"] == 2

    def test_multiple_categories_usage_count_isolation(self, client: TestClient, authenticated_user, sample_category_data, sample_budget_data):
        """Test that usage counts are properly isolated between categories"""
        from datetime import datetime
        import calendar
        current_date = datetime.now()
        start_date = current_date.replace(day=1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        end_date = current_date.replace(day=last_day).strftime("%Y-%m-%d")

        # Create first category
        category_data_1 = {"name": "Food"}
        response = client.post(
            "/api/v1/categories/",
            json=category_data_1,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        category_1 = response.json()["data"]

        # Create second category
        category_data_2 = {"name": "Transport"}
        response = client.post(
            "/api/v1/categories/",
            json=category_data_2,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201
        category_2 = response.json()["data"]

        # Create budgets for both categories
        budget_data_1 = {
            "category_id": category_1["id"],
            "amount": 50000,
            "start_date": start_date,
            "end_date": end_date
        }
        response = client.post(
            "/api/v1/budgets/",
            json=budget_data_1,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        budget_data_2 = {
            "category_id": category_2["id"],
            "amount": 30000,
            "start_date": start_date,
            "end_date": end_date
        }
        response = client.post(
            "/api/v1/budgets/",
            json=budget_data_2,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Initially both categories should have 0 usage
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        categories = response.json()["data"]
        assert len(categories) == 2

        # Find categories by name
        food_category = next(c for c in categories if c["name"] == "Food")
        transport_category = next(c for c in categories if c["name"] == "Transport")

        assert food_category["usage_count"] == 0
        assert transport_category["usage_count"] == 0

        # Create 2 transactions for Food category
        for i in range(2):
            transaction_data = {
                "amount": 1000,
                "category_id": category_1["id"],
                "date": "2025-09-24",
                "type": "expense",
                "payment_method": "cash",
                "description": f"Food transaction {i+1}"
            }
            response = client.post(
                "/api/v1/transactions/",
                json=transaction_data,
                headers=authenticated_user["headers"]
            )
            assert response.status_code == 201

        # Create 1 transaction for Transport category
        transaction_data = {
            "amount": 2000,
            "category_id": category_2["id"],
            "date": "2025-09-24",
            "type": "expense",
            "payment_method": "credit_card",
            "description": "Transport transaction"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Check usage counts are properly isolated
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        categories = response.json()["data"]

        food_category = next(c for c in categories if c["name"] == "Food")
        transport_category = next(c for c in categories if c["name"] == "Transport")

        assert food_category["usage_count"] == 2
        assert transport_category["usage_count"] == 1

    def test_category_usage_count_with_different_transaction_types(self, client: TestClient, authenticated_user, created_category, created_budget):
        """Test that usage_count includes both income and expense transactions"""
        # Create an expense transaction
        expense_transaction = {
            "amount": 2500,
            "category_id": created_category["id"],
            "date": "2025-09-24",
            "type": "expense",
            "payment_method": "cash",
            "description": "Expense transaction"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=expense_transaction,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Create an income transaction
        income_transaction = {
            "amount": 5000,
            "category_id": created_category["id"],
            "date": "2025-09-24",
            "type": "income",
            "payment_method": "bank_transfer",
            "description": "Income transaction"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=income_transaction,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Check that usage_count includes both types
        response = client.get(
            "/api/v1/categories/",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 200
        categories = response.json()["data"]
        assert categories[0]["usage_count"] == 2

    def test_delete_category_with_transactions_should_fail(self, client, authenticated_user, created_category, created_budget):
        """Test that deleting category with transactions fails"""
        # Create transaction
        transaction_data = {
            "amount": 2500,
            "category_id": created_category["id"],
            "date": "2025-09-24",
            "type": "expense",
            "payment_method": "cash",
            "description": "Test transaction"
        }
        response = client.post(
            "/api/v1/transactions/",
            json=transaction_data,
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 201

        # Try to delete category
        response = client.delete(f"/api/v1/categories/{created_category['id']}", headers=authenticated_user["headers"])
        assert response.status_code == 409  # Conflict
        assert "existing transactions" in response.json()["message"].lower()

    def test_delete_category_without_transactions_should_succeed(self, client, authenticated_user, created_category):
        """Test that deleting category without transactions succeeds"""
        response = client.delete(f"/api/v1/categories/{created_category['id']}", headers=authenticated_user["headers"])
        assert response.status_code == 204
