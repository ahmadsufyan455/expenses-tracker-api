from datetime import datetime, date
import calendar


class TestDashboardIntegration:

    def test_get_dashboard_success(self, client, authenticated_user, created_budget):

        # Create income transaction
        income_response = client.post(
            "/api/v1/transactions/",
            json={
                "category_id": created_budget["category_id"],
                "amount": 500000,
                "transaction_date": "2025-10-15",
                "type": "income",
                "payment_method": "bank_transfer",
                "description": "Salary",
            },
            headers=authenticated_user["headers"],
        )
        assert income_response.status_code == 201

        # Create expense transaction
        expense_response = client.post(
            "/api/v1/transactions/",
            json={
                "category_id": created_budget["category_id"],
                "amount": 25000,
                "transaction_date": "2025-10-15",
                "type": "expense",
                "payment_method": "cash",
                "description": "Groceries",
            },
            headers=authenticated_user["headers"],
        )
        assert expense_response.status_code == 201

        response = client.get("/api/v1/dashboard/", headers=authenticated_user["headers"])

        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Dashboard data retrieved successfully"
        assert "data" in data

        dashboard_data = data["data"]

        # Check period
        current_date = datetime.now()
        period_start = date(current_date.year, current_date.month, 1)
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        period_end = date(current_date.year, current_date.month, last_day)
        expected_period = f"{period_start} to {period_end}"
        assert dashboard_data["period"] == expected_period

        # Check summary
        assert "summary" in dashboard_data
        summary = dashboard_data["summary"]
        assert summary["total_income"] == 500000
        assert summary["total_expenses"] == 25000
        assert summary["total_expenses_today"] >= 0
        assert summary["net_balance"] == 475000
        assert summary["savings_rate"] == 95.0

        # Check budgets
        assert "budgets" in dashboard_data
        assert len(dashboard_data["budgets"]) == 1
        budget = dashboard_data["budgets"][0]
        assert budget["category"] == "Food"
        assert budget["spent"] == 25000
        assert budget["limit"] > 0  # Budget exists
        assert budget["percentage"] > 0  # Some percentage calculated

        # Check recent transactions
        assert "recent_transactions" in dashboard_data
        assert len(dashboard_data["recent_transactions"]) == 2

        # Check top expenses
        assert "top_expenses" in dashboard_data
        assert len(dashboard_data["top_expenses"]) == 1
        expense = dashboard_data["top_expenses"][0]
        assert expense["category"] == "Food"
        assert expense["amount"] == 25000
        assert expense["percentage"] == 100.0

    def test_get_dashboard_with_month_parameter(self, client, authenticated_user):
        response = client.get(
            "/api/v1/dashboard/?month=2024-01", headers=authenticated_user["headers"]
        )

        assert response.status_code == 200
        data = response.json()

        assert data["data"]["period"] == "2024-01-01 to 2024-01-31"
        assert data["data"]["summary"]["total_income"] == 0
        assert data["data"]["summary"]["total_expenses"] == 0
        assert data["data"]["summary"]["total_expenses_today"] == 0

    def test_get_dashboard_with_custom_limits(self, client, authenticated_user):
        response = client.get(
            "/api/v1/dashboard/?transaction_limit=1&expense_limit=1",
            headers=authenticated_user["headers"],
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]["recent_transactions"]) <= 1
        assert len(data["data"]["top_expenses"]) <= 1

    def test_get_dashboard_unauthorized(self, client):
        response = client.get("/api/v1/dashboard/")
        assert response.status_code == 401

    def test_get_dashboard_empty_data(self, client):
        # Register a new user with no data
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "empty@example.com",
                "password": "password123",
                "first_name": "Empty",
                "last_name": "User",
            },
        )
        assert register_response.status_code == 201

        login_response = client.post(
            "/api/v1/auth/login", json={"email": "empty@example.com", "password": "password123"}
        )
        assert login_response.status_code == 200
        access_token = login_response.json()["data"]["access_token"]

        response = client.get(
            "/api/v1/dashboard/", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        dashboard_data = data["data"]
        assert dashboard_data["summary"]["total_income"] == 0
        assert dashboard_data["summary"]["total_expenses"] == 0
        assert dashboard_data["summary"]["total_expenses_today"] == 0
        assert dashboard_data["summary"]["net_balance"] == 0
        assert dashboard_data["summary"]["savings_rate"] == 0.0
        assert len(dashboard_data["budgets"]) == 0
        assert len(dashboard_data["recent_transactions"]) == 0
        assert len(dashboard_data["top_expenses"]) == 0

    def test_get_dashboard_with_multiple_categories(self, client, authenticated_user):
        # Create additional categories
        categories = []
        for i in range(3):
            cat_response = client.post(
                f"/api/v1/categories/",
                json={"name": f"Category {i}"},
                headers=authenticated_user["headers"],
            )
            assert cat_response.status_code == 201
            categories.append(cat_response.json()["data"])

        current_date = datetime.now()
        start_date = current_date.replace(day=1).strftime("%Y-%m-%d")
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        end_date = current_date.replace(day=last_day).strftime("%Y-%m-%d")

        # Create budgets and transactions for each category
        for i, category in enumerate(categories):
            # Create budget
            client.post(
                "/api/v1/budgets/",
                json={
                    "category_id": category["id"],
                    "amount": 100000 * (i + 1),
                    "start_date": start_date,
                    "end_date": end_date,
                },
                headers=authenticated_user["headers"],
            )

            # Create expense
            transaction_date = datetime.now().strftime("%Y-%m-%d")
            client.post(
                "/api/v1/transactions/",
                json={
                    "category_id": category["id"],
                    "amount": 50000 * (i + 1),
                    "transaction_date": transaction_date,
                    "type": "expense",
                    "payment_method": "cash",
                },
                headers=authenticated_user["headers"],
            )

        response = client.get("/api/v1/dashboard/", headers=authenticated_user["headers"])

        assert response.status_code == 200
        data = response.json()

        dashboard_data = data["data"]
        assert len(dashboard_data["budgets"]) == 3  # 3 new categories
        assert len(dashboard_data["top_expenses"]) == 3  # Limited to 3
