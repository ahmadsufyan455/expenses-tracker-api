from fastapi import APIRouter, status, Query
from app.core.dependencies import TransactionServiceDep, CurrentUserDep
from app.core.responses import SuccessResponse, PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.constants.messages import TransactionMessages

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_transactions(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("date", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc")
) -> PaginatedResponse:
    skip = (page - 1) * per_page

    transactions, total = transaction_service.get_user_transactions_with_category(
        current_user["user_id"],
        skip,
        per_page,
        sort_by,
        sort_order
    )
    transaction_responses = [TransactionResponse.model_validate(transaction) for transaction in transactions]
    return PaginatedResponse(
        message=TransactionMessages.RETRIEVED_SUCCESS.value,
        data=transaction_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    transaction_data: TransactionCreate
) -> SuccessResponse:
    transaction = transaction_service.create_transaction(current_user["user_id"], transaction_data)
    transaction_response = TransactionResponse.model_validate(transaction)
    return SuccessResponse(message=TransactionMessages.CREATED_SUCCESS.value, data=transaction_response)


@router.put("/{transaction_id}", status_code=status.HTTP_200_OK)
async def update_transaction(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    transaction_id: int,
    transaction_data: TransactionUpdate
) -> SuccessResponse:
    transaction = transaction_service.update_transaction(transaction_id, current_user["user_id"], transaction_data)
    transaction_response = TransactionResponse.model_validate(transaction)
    return SuccessResponse(message=TransactionMessages.UPDATED_SUCCESS.value, data=transaction_response)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_service: TransactionServiceDep,
    current_user: CurrentUserDep,
    transaction_id: int
):
    transaction_service.delete_transaction(transaction_id, current_user["user_id"])
