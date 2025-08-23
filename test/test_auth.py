from .utils import *
from jose import jwt
from starlette import status
from routers.auth import get_db, authenticate_user, create_access_token, ALGORITHM, SECRET_KEY, get_current_user
from datetime import datetime, timezone

app.dependency_overrides[get_db] = override_get_db

def test_create_access_token(test_user):
    token = create_access_token(str(test_user.id), test_user.email)
    assert token is not None

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token.get("user_id") == str(test_user.id)
    assert decoded_token.get("email") == test_user.email
    assert decoded_token.get("exp") is not None
    assert decoded_token.get("exp") > datetime.now().timestamp()

def test_authenticate_user(test_user):
    db = TestSessionLocal()
    user = authenticate_user(db, test_user.email, 'test123')

    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email
    assert user.first_name == test_user.first_name
    assert user.last_name == test_user.last_name
    assert user.hashed_password == test_user.hashed_password

    db.close()

def test_authenticate_user_with_wrong_email():
    db = TestSessionLocal()

    with pytest.raises(Exception) as e:
        authenticate_user(db, "wrong_email@test.com", "test123")

    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.message == "Login failed"
    assert e.value.error == "User not found"
    db.close()

def test_authenticate_user_with_wrong_password(test_user):
    db = TestSessionLocal()
    with pytest.raises(Exception) as e:
        authenticate_user(db, test_user.email, "wrong_password")

    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.message == "Login failed"
    assert e.value.error == "Incorrect password"

    db.close()

@pytest.mark.asyncio
async def test_get_current_user(test_user):
    token = create_access_token(str(test_user.id), test_user.email)
    user = await get_current_user(token)
    assert user is not None
    assert user.get("user_id") == str(test_user.id)
    assert user.get("email") == test_user.email

@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token():
    token = "invalid_token"
    with pytest.raises(Exception) as e:
        await get_current_user(token)

    assert e.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert e.value.message == "Invalid token"

def test_register_user():
    request_body = {
        "email": "test2@test.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "test123"
    }
    responses = client.post("/auth/register", json=request_body)
    assert responses.status_code == status.HTTP_201_CREATED
    assert responses.json().get("message") == "User registered successfully"

    db = TestSessionLocal()
    user = db.query(User).filter(User.email == request_body.get("email")).first()

    assert user is not None
    assert user.email == request_body.get("email")
    assert user.first_name == request_body.get("first_name")
    assert user.last_name == request_body.get("last_name")
    assert user.hashed_password is not None

    db.close()

def test_register_user_with_existing_email():
    request_body = {
        "email": "test2@test.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "test123"
    }
    responses = client.post("/auth/register", json=request_body)
    assert responses.status_code == status.HTTP_400_BAD_REQUEST
    assert responses.json().get("message") == "Registration failed"
    assert responses.json().get("error") == "Email already registered"

def test_login_user():
    request_body = {
        "email": "test2@test.com",
        "password": "test123"
    }
    responses = client.post("/auth/login", json=request_body)
    assert responses.status_code == status.HTTP_200_OK
    assert responses.json() == {
        "message": "Login successful",
        "data": {
            "access_token": responses.json().get("data").get("access_token"),
            "token_type": "bearer",
            "expires_in": 60 * 60
        }
    }

def test_login_user_with_wrong_email():
    request_body = {
        "email": "wrong_email@test.com",
        "password": "test123"
    }
    responses = client.post("/auth/login", json=request_body)
    assert responses.status_code == status.HTTP_401_UNAUTHORIZED
    assert responses.json().get("message") == "Login failed"
    assert responses.json().get("error") == "User not found"

def test_login_user_with_wrong_password():
    request_body = {
        "email": "test2@test.com",
        "password": "wrong_password"
    }
    responses = client.post("/auth/login", json=request_body)
    assert responses.status_code == status.HTTP_401_UNAUTHORIZED
    assert responses.json().get("message") == "Login failed"
    assert responses.json().get("error") == "Incorrect password"
