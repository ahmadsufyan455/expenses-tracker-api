import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.base_response import SuccessResponse, ErrorResponse
from db.database import SessionLocal
from db.models import User

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class RegisterRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


def create_access_token(user_id: str, email: str, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(db: db_dependency, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ErrorResponse(message="Login failed", error="User not found", status_code=status.HTTP_401_UNAUTHORIZED)
    if not pwd_context.verify(password, user.hashed_password):
        raise ErrorResponse(message="Login failed", error="Incorrect password",
                            status_code=status.HTTP_401_UNAUTHORIZED)
    return user


# JWT token validator and user extractor for protected routes.
# Decodes JWT token, validates user data, and returns user information.
# Used as a dependency to protect routes requiring authentication.
async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        email = payload.get("email")
        if user_id is None or email is None:
            raise ErrorResponse(message="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)
        return {
            "user_id": user_id,
            "email": email
        }
    except JWTError:
        raise ErrorResponse(message="Invalid token", status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: db_dependency):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise ErrorResponse(message="Registration failed", error="Email already registered",
                            status_code=status.HTTP_400_BAD_REQUEST)

    user = User(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=pwd_context.hash(request.password)
    )

    db.add(user)
    db.commit()

    return SuccessResponse(message="User registered successfully")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(db: db_dependency, request: LoginRequest):
    user = authenticate_user(db, request.email, request.password)
    access_token = create_access_token(str(user.id), user.email)

    token = Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return SuccessResponse(message="Login successful", data=token)
