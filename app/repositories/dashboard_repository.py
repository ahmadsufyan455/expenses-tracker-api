from typing import List, Optional, Dict, Any
import calendar
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, case
from datetime import date
from app.models.transaction import Transaction, TransactionType
from app.models.budget import Budget
from app.models.category import Category


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_monthly_summary(
        self, user_id: int, period_start: date, period_end: date
    ) -> Dict[str, int]:
        income_sum = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.INCOME,
                    Transaction.transaction_date >= period_start,
                    Transaction.transaction_date <= period_end,
                )
            )
            .scalar()
            or 0
        )

        expense_sum = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.transaction_date >= period_start,
                    Transaction.transaction_date <= period_end,
                )
            )
            .scalar()
            or 0
        )

        today = date.today()
        if period_start <= today <= period_end:
            expense_sum_today = (
                self.db.query(func.sum(Transaction.amount))
                .filter(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.type == TransactionType.EXPENSE,
                        Transaction.transaction_date == today,
                    ),
                )
                .scalar()
                or 0
            )
        else:
            expense_sum_today = 0

        return {
            "total_income": income_sum,
            "total_expenses": expense_sum,
            "total_expenses_today": expense_sum_today,
        }

    def get_budgets_with_spending(
        self, user_id: int, period_start: date, period_end: date, limit: int = 3
    ) -> List[Dict[str, Any]]:
        budgets = (
            self.db.query(
                Budget,
                Category.name,
                func.coalesce(
                    func.sum(
                        case(
                            (Transaction.type == TransactionType.EXPENSE, Transaction.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("spent"),
            )
            .join(Category, Budget.category_id == Category.id)
            .outerjoin(
                Transaction,
                and_(
                    Transaction.category_id == Budget.category_id,
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.transaction_date.between(Budget.start_date, Budget.end_date),
                ),
            )
            .filter(
                and_(
                    Budget.user_id == user_id,
                    # Budget period overlaps with the requested month
                    Budget.start_date <= period_end,
                    Budget.end_date >= period_start,
                )
            )
            .group_by(Budget.id, Category.name)
            .order_by(func.coalesce(func.max(Transaction.transaction_date), "1900-01-01").desc())
            .limit(limit)
            .all()
        )

        result = []
        for budget, category_name, spent in budgets:
            result.append(
                {
                    "category": category_name,
                    "spent": int(spent),
                    "limit": budget.amount,
                    "percentage": (
                        round((spent / budget.amount) * 100, 2) if budget.amount > 0 else 0
                    ),
                }
            )

        return result

    def get_recent_transactions(
        self,
        user_id: int,
        limit: int = 5,
        period_start: Optional[date] = None,
        period_end: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        query = (
            self.db.query(Transaction, Category.name.label("category_name"))
            .join(Category, Transaction.category_id == Category.id)
            .filter(Transaction.user_id == user_id)
        )

        # Add month/year filtering if provided
        if period_start is not None and period_end is not None:
            query = query.filter(
                and_(
                    Transaction.transaction_date >= period_start,
                    Transaction.transaction_date <= period_end,
                )
            )

        transactions = query.order_by(Transaction.transaction_date.desc()).limit(limit).all()

        result = []
        for transaction, category_name in transactions:
            result.append(
                {
                    "id": transaction.id,
                    "amount": transaction.amount,
                    "type": transaction.type.value,
                    "category": category_name,
                    "transaction_date": transaction.transaction_date,
                }
            )

        return result

    def get_top_expenses(
        self, user_id: int, period_start: date, period_end: date, limit: int = 3
    ) -> List[Dict[str, Any]]:
        expense_query = (
            self.db.query(Category.name, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.transaction_date >= period_start,
                    Transaction.transaction_date <= period_end,
                )
            )
            .group_by(Category.name)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(limit)
            .all()
        )

        total_expenses = sum(amount for _, amount in expense_query)

        result = []
        for category_name, amount in expense_query:
            result.append(
                {
                    "category": category_name,
                    "amount": amount,
                    "percentage": (
                        round((amount / total_expenses) * 100, 2) if total_expenses > 0 else 0
                    ),
                }
            )

        return result
