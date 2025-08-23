import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from db.database import Base
from main import app
from db.models import User
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