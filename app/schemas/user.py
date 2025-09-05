from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
