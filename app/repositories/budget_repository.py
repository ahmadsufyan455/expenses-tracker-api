from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from .base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, db: Session):
        super().__init__(db, Budget)

    def get_by_user_and_category_and_month(
        self,
        user_id: int,
        category_id: int,
        month: date
    ) -> Optional[Budget]:
        return self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.month == month
        ).first()

    def get_budgets_with_spending_data(self, user_id: int) -> List[dict]:
        """Get all budgets for a user with current month spending data"""
        query = self.db.query(
            Budget,
            func.coalesce(func.sum(Transaction.amount), 0).label('total_spent')
        ).outerjoin(
            Transaction,
            (Budget.user_id == Transaction.user_id) &
            (Budget.category_id == Transaction.category_id) &
            (Transaction.type == TransactionType.EXPENSE) &
            (func.extract('year', Transaction.created_at) == func.extract('year', Budget.month)) &
            (func.extract('month', Transaction.created_at) == func.extract('month', Budget.month))
        ).filter(
            Budget.user_id == user_id
        ).group_by(Budget.id)

        results = []
        for budget, total_spent in query.all():
            results.append({
                'budget': budget,
                'total_spent': int(total_spent) if total_spent else 0
            })

        return results
