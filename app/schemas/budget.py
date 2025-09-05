from typing import Optional
from pydantic import BaseModel, Field
from datetime import date


class BudgetBase(BaseModel):
    category_id: int
    amount: int = Field(gt=0, description="Amount must be greater than 0")


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
