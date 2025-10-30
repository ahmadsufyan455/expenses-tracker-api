import calendar
from typing import Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardData,
    DashboardSummary,
    BudgetOverview,
    RecentTransaction,
    TopExpense,
)
from app.constants.messages import DashboardMessages


class DashboardService:
    def __init__(self, db: Session):
        self.dashboard_repo = DashboardRepository(db)

    def get_dashboard_data(
        self,
        user_id: int,
        month: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_limit: int = 5,
        expense_limit: int = 3,
        budget_limit: int = 3,
    ) -> DashboardData:
        if start_date and end_date:
            period_start = start_date
            period_end = end_date
        elif month:
            try:
                year, month_num = map(int, month.split("-"))
                period_start = date(year, month_num, 1)
                last_day = calendar.monthrange(year, month_num)[1]
                period_end = date(year, month_num, last_day)
            except ValueError:
                raise ValueError(DashboardMessages.INVALID_MONTH_FORMAT.value)
        else:
            now = datetime.now()
            period_start = date(now.year, now.month, 1)
            last_day = calendar.monthrange(now.year, now.month)[1]
            period_end = date(now.year, now.month, last_day)

        # Get monthly summary
        summary_data = self.dashboard_repo.get_monthly_summary(user_id, period_start, period_end)

        # Calculate net balance and savings rate
        net_balance = summary_data["total_income"] - summary_data["total_expenses"]

        if summary_data["total_income"] > 0:
            savings_rate = round((net_balance / summary_data["total_income"]) * 100, 2)
        else:
            savings_rate = 0.0

        summary = DashboardSummary(
            total_income=summary_data["total_income"],
            total_expenses=summary_data["total_expenses"],
            total_expenses_today=summary_data["total_expenses_today"],
            net_balance=net_balance,
            savings_rate=savings_rate,
        )

        # Get budgets with spending
        budget_data = self.dashboard_repo.get_budgets_with_spending(
            user_id, period_start, period_end, budget_limit
        )
        budgets = [BudgetOverview(**budget) for budget in budget_data]

        # Get recent transactions with configurable limit, filtered by month if provided
        transaction_data = self.dashboard_repo.get_recent_transactions(
            user_id, transaction_limit, period_start, period_end
        )
        recent_transactions = [RecentTransaction(**trans) for trans in transaction_data]

        # Get top expenses with configurable limit
        expense_data = self.dashboard_repo.get_top_expenses(
            user_id, period_start, period_end, expense_limit
        )
        top_expenses = [TopExpense(**expense) for expense in expense_data]

        # Format period
        period = f"{period_start} to {period_end}"

        return DashboardData(
            period=period,
            summary=summary,
            budgets=budgets,
            recent_transactions=recent_transactions,
            top_expenses=top_expenses,
        )
