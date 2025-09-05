from fastapi import APIRouter, status
from app.core.dependencies import TransactionServiceDep, CurrentUserDep
from app.core.responses import SuccessResponse
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_transactions(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep
) -> SuccessResponse:
    transactions = transaction_service.get_user_transactions(current_user["user_id"])
    transaction_responses = [TransactionResponse.model_validate(transaction) for transaction in transactions]
    return SuccessResponse(message="Transactions retrieved successfully", data=transaction_responses)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    transaction_data: TransactionCreate
) -> SuccessResponse:
    transaction = transaction_service.create_transaction(current_user["user_id"], transaction_data)
    transaction_response = TransactionResponse.model_validate(transaction)
    return SuccessResponse(message="Transaction created successfully", data=transaction_response)


@router.put("/{transaction_id}/update", status_code=status.HTTP_200_OK)
async def update_transaction(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    transaction_id: int,
    transaction_data: TransactionUpdate
) -> SuccessResponse:
    transaction = transaction_service.update_transaction(transaction_id, current_user["user_id"], transaction_data)
    transaction_response = TransactionResponse.model_validate(transaction)
    return SuccessResponse(message="Transaction updated successfully", data=transaction_response)


@router.delete("/{transaction_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    transaction_id: int
):
    transaction_service.delete_transaction(transaction_id, current_user["user_id"])
