from datetime import datetime
from fastapi import APIRouter, Depends, status
from core.base_response import SuccessResponse, ErrorResponse
from db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from routers.auth import get_current_user
from typing import Annotated
from core.validation import validate_user
from datetime import date
from db.models import Budget
from pydantic import BaseModel, field_validator

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class BudgetResponse(BaseModel):
    id: int
    category_id: int
    amount: int
    month: date

    model_config = {
        "from_attributes": True
    }


class BudgetRequest(BaseModel):
    category_id: int
    amount: int
    month: str


def get_budget_response(budgets):
    for budget in budgets:
        yield BudgetResponse.model_validate(budget)


def parse_month(month: str):
    try:
        # Parse year-month and set to first day of month
        return datetime.strptime(
            month, "%Y-%m").replace(day=1).date()
    except ValueError:
        raise ErrorResponse(
            message="Invalid month format. Use YYYY-MM format (e.g., '2025-09')",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_budgets(db: db_dependency, user: user_dependency):
    validate_user(user)
    budgets = db.query(Budget).filter(
        Budget.user_id == user.get("user_id")).all()
    budget_responses = get_budget_response(budgets)
    return SuccessResponse(message="Budgets fetched successfully", data=budget_responses)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def create_budget(db: db_dependency, user: user_dependency, request: BudgetRequest):
    validate_user(user)

    month_date = parse_month(request.month)

    budget = Budget(
        user_id=user.get("user_id"),
        category_id=request.category_id,
        amount=request.amount,
        month=month_date)

    db.add(budget)

    try:
        db.commit()
        db.refresh(budget)
    except IntegrityError:
        db.rollback()
        raise ErrorResponse(
            message="Budget already exists for this category and month",
            status_code=status.HTTP_409_CONFLICT
        )

    budget_response = BudgetResponse.model_validate(budget)
    return SuccessResponse(message="Budget created successfully", data=budget_response)


@router.put("/{budget_id}/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_budget(db: db_dependency, user: user_dependency, budget_id: int, request: BudgetRequest):
    validate_user(user)

    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise ErrorResponse(message="Budget not found",
                            status_code=status.HTTP_404_NOT_FOUND)

    month_date = parse_month(request.month)

    budget.category_id = request.category_id
    budget.amount = request.amount
    budget.month = month_date

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ErrorResponse(
            message="Budget already exists for this category and month",
            status_code=status.HTTP_409_CONFLICT
        )


@router.delete("/{budget_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(db: db_dependency, user: user_dependency, budget_id: int):
    validate_user(user)

    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise ErrorResponse(message="Budget not found",
                            status_code=status.HTTP_404_NOT_FOUND)

    db.delete(budget)
    db.commit()
