from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from db.database import get_db
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from core.validation import validate_user
from db.models import Budget, Transaction, Category, TransactionType, PaymentMethod
from datetime import datetime
from core.base_response import SuccessResponse, ErrorResponse
from uuid import UUID

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TransactionResponse(BaseModel):
    id: UUID
    category_id: int
    amount: int
    type: TransactionType
    payment_method: PaymentMethod
    description: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TransactionRequest(BaseModel):
    category_id: int
    amount: int
    type: TransactionType
    payment_method: PaymentMethod
    description: Optional[str] = None


def get_transaction_reponse(transactions):
    for transaction in transactions:
        yield TransactionResponse.model_validate(transaction)


@router.get("/", status_code=status.HTTP_200_OK)
def get_transactions(db: db_dependency, user: user_dependency):
    validate_user(user)
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.get("user_id")).all()
    transaction_responses = get_transaction_reponse(transactions)
    return SuccessResponse(message="Transactions retrieved successfully", data=transaction_responses)


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_transaction(db: db_dependency, user: user_dependency, request: TransactionRequest):
    validate_user(user)

    category = db.query(Category).filter(
        Category.id == request.category_id).first()
    if not category:
        raise ErrorResponse(message="Category not found",
                            status_code=status.HTTP_404_NOT_FOUND)

    current_month = datetime.now().date().replace(day=1)

    budget = db.query(Budget).filter(
        Budget.user_id == user.get("user_id"),
        Budget.category_id == request.category_id,
        Budget.month == current_month
    ).first()

    if not budget and request.type == TransactionType.EXPENSE:
        raise ErrorResponse(
            message=f"Please set a budget for {category.name} category for {current_month.strftime('%B %Y')} before adding expenses",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    transaction = Transaction(
        user_id=user.get("user_id"),
        category_id=request.category_id,
        amount=request.amount,
        type=request.type,
        payment_method=request.payment_method,
        description=request.description,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    transaction_response = TransactionResponse.model_validate(transaction)

    return SuccessResponse(message="Transaction created successfully", data=transaction_response)


@router.put("/{transaction_id}/update", status_code=status.HTTP_204_NO_CONTENT)
def update_transaction(db: db_dependency, user: user_dependency, transaction_id: UUID, request: TransactionRequest):
    validate_user(user)

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id).first()
    if not transaction:
        raise ErrorResponse(message="Transaction not found",
                            status_code=status.HTTP_404_NOT_FOUND)

    transaction.category_id = request.category_id
    transaction.amount = request.amount
    transaction.type = request.type
    transaction.payment_method = request.payment_method
    transaction.description = request.description

    db.commit()


@router.delete("/{transaction_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(db: db_dependency, user: user_dependency, transaction_id: UUID):
    validate_user(user)

    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id).first()
    if not transaction:
        raise ErrorResponse(message="Transaction not found",
                            status_code=status.HTTP_404_NOT_FOUND)

    db.delete(transaction)
    db.commit()
