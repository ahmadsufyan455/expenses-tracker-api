from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.constants.messages import ValidationMessages


class BudgetBase(BaseModel):
    category_id: int
    amount: int = Field(gt=0, description=ValidationMessages.INVALID_AMOUNT.value)


class BudgetCreate(BudgetBase):
    month: str


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[int] = Field(None, gt=0)
    month: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}$')


class BudgetResponse(BudgetBase):
    id: int
    month: date

    model_config = {
        "from_attributes": True
    }
