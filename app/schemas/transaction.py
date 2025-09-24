from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.models.transaction import TransactionType, PaymentMethod
from .category import CategoryResponse


class TransactionBase(BaseModel):
    amount: int
    date: date
    type: TransactionType
    payment_method: PaymentMethod
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    category_id: int
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[int] = None
    date: Optional[date] = None
    category_id: Optional[int] = None
    type: Optional[TransactionType] = None
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
