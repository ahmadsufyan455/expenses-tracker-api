from typing import Optional
from fastapi import APIRouter, status, Query

from app.core.dependencies import CurrentUserDep, DashboardServiceDep
from app.core.responses import SuccessResponse
from app.constants.messages import DashboardMessages

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_dashboard(
    current_user: CurrentUserDep,
    dashboard_service: DashboardServiceDep,
    month: Optional[str] = Query(None, description="Month in YYYY-MM format"),
    transaction_limit: int = Query(5, ge=1, le=50, description="Number of recent transactions to return"),
    expense_limit: int = Query(3, ge=1, le=10, description="Number of top expense categories to return"),
    budget_limit: int = Query(3, ge=1, le=10, description="Number of top budgets to return")
) -> SuccessResponse:
    dashboard_data = dashboard_service.get_dashboard_data(
        user_id=current_user["user_id"],
        month=month,
        transaction_limit=transaction_limit,
        expense_limit=expense_limit,
        budget_limit=budget_limit
    )

    return SuccessResponse(
        message=DashboardMessages.RETRIEVED_SUCCESS.value,
        data=dashboard_data.model_dump()
    )
