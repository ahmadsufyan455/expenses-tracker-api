from pydantic import BaseModel
from typing import List
from datetime import date


class DashboardSummary(BaseModel):
    total_income: int
    total_expenses: int
    total_expenses_today: int
    net_balance: int
    savings_rate: float


class BudgetOverview(BaseModel):
    category: str
    spent: int
    limit: int
    percentage: float


class RecentTransaction(BaseModel):
    id: int
    amount: int
    type: str
    category: str
    transaction_date: date


class TopExpense(BaseModel):
    category: str
    amount: int
    percentage: float


class DashboardData(BaseModel):
    period: str
    summary: DashboardSummary
    budgets: List[BudgetOverview]
    recent_transactions: List[RecentTransaction]
    top_expenses: List[TopExpense]