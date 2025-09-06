import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.config.database import get_db
from app.models.base import Base

# Test database URL (SQLite in-memory database)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing"""
    return {
        "name": "Food"
    }


@pytest.fixture
def sample_budget_data():
    """Sample budget data for testing"""
    from datetime import datetime
    current_month = datetime.now().strftime("%Y-%m")
    return {
        "category_id": 1,
        "amount": 50000,  # $500.00 in cents
        "month": current_month
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing"""
    return {
        "amount": 2500,  # $25.00 in cents
        "category_id": 1,
        "type": "expense",
        "payment_method": "cash",
        "description": "Lunch at restaurant"
    }


@pytest.fixture
def authenticated_user(client, sample_user_data):
    """Create a user and return authentication token"""
    # Register user
    register_response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert register_response.status_code == 201
    user_data = register_response.json()["data"]

    # Login and get token
    login_data = {
        "email": sample_user_data["email"],
        "password": sample_user_data["password"]
    }
    login_response = client.post("/api/v1/auth/login", json=login_data)
    assert login_response.status_code == 200

    token_data = login_response.json()["data"]
    return {
        "token": token_data["access_token"],
        "user_id": user_data["id"],  # Get user_id from registration response
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"}
    }


@pytest.fixture
def created_category(client, authenticated_user, sample_category_data):
    """Create a category and return its data"""
    response = client.post(
        "/api/v1/categories/",
        json=sample_category_data,
        headers=authenticated_user["headers"]
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.fixture
def created_budget(client, authenticated_user, created_category, sample_budget_data):
    """Create a budget and return its data"""
    budget_data = sample_budget_data.copy()
    budget_data["category_id"] = created_category["id"]

    response = client.post(
        "/api/v1/budgets/",
        json=budget_data,
        headers=authenticated_user["headers"]
    )
    assert response.status_code == 201
    return response.json()["data"]
