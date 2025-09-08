from pydantic import BaseModel
from typing import Optional

from app.models.transaction import TransactionType, PaymentMethod


class TransactionBase(BaseModel):
    amount: int
    type: TransactionType
    payment_method: PaymentMethod
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    category_id: int
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[int] = None
    category_id: Optional[int] = None
    type: Optional[TransactionType] = None
    payment_method: Optional[PaymentMethod] = None
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    category_name: str

    model_config = {
        "from_attributes": True
    }
