import uuid
from datetime import datetime, date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base
from db.models import User, Category, Transaction, TransactionType, PaymentMethod, Budget, Attachment
from main import app
from routers.auth import pwd_context

engine = create_engine(
    "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


TEST_USER_ID = uuid.UUID("b885a6ed-1ec2-4c34-8df4-2ba2a6974c1b")


def override_get_current_user():
    return {"user_id": TEST_USER_ID, "email": "testuser@gmail.com"}


client = TestClient(app)


@pytest.fixture
def test_user():
    db = TestSessionLocal()
    db.query(User).delete()

    user = User(
        email="test@test.com",
        first_name="Test",
        last_name="User",
        hashed_password=pwd_context.hash("test123")
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.query(User).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_category():
    db = TestSessionLocal()
    db.query(Category).delete()

    category = Category(name="Test Category", user_id=TEST_USER_ID)
    db.add(category)
    db.commit()
    db.refresh(category)

    yield category

    db.query(Category).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_transaction(test_category):
    db = TestSessionLocal()

    transaction = Transaction(
        user_id=TEST_USER_ID,
        category_id=test_category.id,
        amount=10000,
        type=TransactionType.INCOME,
        payment_method=PaymentMethod.CASH,
        description="Test Transaction",
        created_at=datetime.now()
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    yield transaction

    db.query(Transaction).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_budget(test_category):
    db = TestSessionLocal()

    budget = Budget(
        user_id=TEST_USER_ID,
        category_id=test_category.id,
        amount=500000,
        month=date(2025, 9, 1)  # September 2025
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    yield budget

    db.query(Budget).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_attachment(test_transaction):
    db = TestSessionLocal()

    attachment = Attachment(
        transaction_id=test_transaction.id,
        file_path="test_receipt.jpg",
        uploaded_at=datetime.now()
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    yield attachment

    db.query(Attachment).delete()
    db.commit()
    db.close()
