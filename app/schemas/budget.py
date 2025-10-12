from typing import Optional
from pydantic import BaseModel, Field, field_validator
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
    start_date: date
    end_date: date
    prediction_enabled: Optional[bool] = False
    prediction_type: Optional[PredictionType] = None
    prediction_days_count: Optional[int] = Field(None, ge=1, le=31)

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start_date(cls, v, info):
        if info.data.get("start_date") and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[int] = Field(None, gt=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    prediction_enabled: Optional[bool] = None
    prediction_type: Optional[PredictionType] = None
    prediction_days_count: Optional[int] = Field(None, ge=1, le=31)

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start_date(cls, v, info):
        if v is not None and info.data.get("start_date") is not None and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class BudgetResponse(BudgetBase):
    id: int
    start_date: date
    end_date: date
    status: int
    prediction_enabled: bool
    prediction_type: Optional[PredictionType] = None
    prediction_days_count: Optional[int] = None
    prediction: Optional[BudgetPrediction] = None

    model_config = {"from_attributes": True}
