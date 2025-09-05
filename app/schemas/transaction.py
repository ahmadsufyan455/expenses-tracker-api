from pydantic import BaseModel
from typing import Optional

from app.models.transaction import TransactionType, PaymentMethod


class TransactionBase(BaseModel):
    amount: int
    category_id: int
    type: TransactionType
    payment_method: PaymentMethod
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[int] = None
    category_id: Optional[int] = None
    type: Optional[TransactionType] = None
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int

    model_config = {
        "from_attributes": True
    }
