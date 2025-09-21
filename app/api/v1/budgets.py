from fastapi import APIRouter, status, Query

from app.core.dependencies import BudgetServiceDep, CurrentUserDep
from app.core.responses import SuccessResponse, PaginatedResponse
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.constants.messages import BudgetMessages

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_budgets(
    budget_service: BudgetServiceDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc")
) -> PaginatedResponse:
    skip = (page - 1) * per_page

    budgets_data, total = budget_service.get_user_budgets(
        current_user["user_id"],
        skip,
        per_page,
        sort_by,
        sort_order
    )
    budget_responses = [BudgetResponse.model_validate(budget_data) for budget_data in budgets_data]
    return PaginatedResponse(
        message=BudgetMessages.RETRIEVED_SUCCESS.value,
        data=budget_responses,
        total=total,
        page=page,
        per_page=per_page
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    budget_service: BudgetServiceDep,
    current_user: CurrentUserDep
) -> SuccessResponse:
    budget = budget_service.create_budget(current_user["user_id"], budget_data)
    budget_response = BudgetResponse.model_validate(budget)
    return SuccessResponse(
        message=BudgetMessages.CREATED_SUCCESS.value,
        data=budget_response
    )


@router.put("/{budget_id}", status_code=status.HTTP_200_OK)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    budget_service: BudgetServiceDep,
    current_user: CurrentUserDep
) -> SuccessResponse:
    budget = budget_service.update_budget(budget_id, current_user["user_id"], budget_data)
    budget_response = BudgetResponse.model_validate(budget)
    return SuccessResponse(
        message=BudgetMessages.UPDATED_SUCCESS.value,
        data=budget_response
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    budget_service: BudgetServiceDep,
    current_user: CurrentUserDep
):
    budget_service.delete_budget(budget_id, current_user["user_id"])
