from fastapi.testclient import TestClient

from app.constants.messages import AuthMessages


class TestAuthEndpoints:
    """Integration tests for authentication endpoints"""

    def test_register_success(self, client: TestClient, sample_user_data):
        """Test successful user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == 201
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "data" in data
        assert data["message"] == AuthMessages.REGISTER_SUCCESS.value

        # Check user data
        user_data = data["data"]
        assert user_data["email"] == sample_user_data["email"]
        assert user_data["first_name"] == sample_user_data["first_name"]
        assert user_data["last_name"] == sample_user_data["last_name"]
        assert "id" in user_data
        assert "hashed_password" not in user_data  # Password should not be returned

    def test_register_duplicate_email(self, client: TestClient, sample_user_data):
        """Test registration with duplicate email"""
        # Register first user
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 201

        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert response.status_code == 409  # Conflict

        data = response.json()
        assert data["message"] == AuthMessages.ALREADY_EXISTS.value

    def test_register_invalid_email(self, client: TestClient, sample_user_data):
        """Test registration with invalid email"""
        invalid_data = sample_user_data.copy()
        invalid_data["email"] = "invalid-email"

        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_register_short_password(self, client: TestClient, sample_user_data):
        """Test registration with short password"""
        invalid_data = sample_user_data.copy()
        invalid_data["password"] = "123"  # Too short

        response = client.post("/api/v1/auth/register", json=invalid_data)
        assert response.status_code == 400  # Bad request

    def test_register_missing_fields(self, client: TestClient):
        """Test registration with missing required fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing other required fields
        }

        response = client.post("/api/v1/auth/register", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_login_success(self, client: TestClient, sample_user_data):
        """Test successful user login"""
        # First register a user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == 201

        # Now login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "message" in data
        assert "data" in data
        assert data["message"] == AuthMessages.LOGIN_SUCCESS.value

        # Check token data
        token_data = data["data"]
        assert "access_token" in token_data
        assert "token_type" in token_data
        assert "expires_in" in token_data
        assert token_data["token_type"] == "bearer"
        assert isinstance(token_data["access_token"], str)
        assert len(token_data["access_token"]) > 0
        assert isinstance(token_data["expires_in"], int)

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 404  # Not Found (as per your auth service)
        data = response.json()
        assert data["message"] == AuthMessages.USER_NOT_FOUND.value

    def test_login_invalid_password(self, client: TestClient, sample_user_data):
        """Test login with wrong password"""
        # First register a user
        register_response = client.post("/api/v1/auth/register", json=sample_user_data)
        assert register_response.status_code == 201

        # Try login with wrong password
        login_data = {
            "email": sample_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401  # Unauthorized
        data = response.json()
        assert data["message"] == AuthMessages.INVALID_PASSWORD.value

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields"""
        incomplete_data = {
            "email": "test@example.com"
            # Missing password
        }

        response = client.post("/api/v1/auth/login", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 404  # Treated as user not found
