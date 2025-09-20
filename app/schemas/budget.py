from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.constants.messages import ValidationMessages
from app.models.budget import PredictionType


class BudgetPrediction(BaseModel):
    daily_allowance: int
    remaining_budget: int
    days_remaining: int
    prediction_type: PredictionType


class BudgetBase(BaseModel):
    category_id: int
    amount: int = Field(gt=0, description=ValidationMessages.INVALID_AMOUNT.value)


class BudgetCreate(BudgetBase):
    month: str
    prediction_enabled: Optional[bool] = False
    prediction_type: Optional[PredictionType] = None
    prediction_days_count: Optional[int] = Field(None, ge=1, le=31)


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[int] = Field(None, gt=0)
    month: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}$')
    prediction_enabled: Optional[bool] = None
    prediction_type: Optional[PredictionType] = None
    prediction_days_count: Optional[int] = Field(None, ge=1, le=31)


class BudgetResponse(BudgetBase):
    id: int
    month: date
    prediction_enabled: bool
    prediction_type: Optional[PredictionType] = None
    prediction_days_count: Optional[int] = None
    prediction: Optional[BudgetPrediction] = None

    model_config = {
        "from_attributes": True
    }
