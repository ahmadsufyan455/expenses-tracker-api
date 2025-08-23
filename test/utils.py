import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base
from db.models import User, Category
from main import app
from routers.auth import pwd_context

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"user_id": uuid.UUID("b885a6ed-1ec2-4c34-8df4-2ba2a6974c1b"), "email": "testuser@gmail.com"}


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

    category = Category(name="Test Category", user_id=uuid.UUID("b885a6ed-1ec2-4c34-8df4-2ba2a6974c1b"))
    db.add(category)
    db.commit()
    db.refresh(category)

    yield category

    db.query(Category).delete()
    db.commit()
    db.close()
