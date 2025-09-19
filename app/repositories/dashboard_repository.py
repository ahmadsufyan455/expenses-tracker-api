from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, case
from datetime import datetime, date
from app.models.transaction import Transaction, TransactionType
from app.models.budget import Budget
from app.models.category import Category


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict[str, int]:
        income_sum = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.INCOME,
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            )
        ).scalar() or 0

        expense_sum = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            )
        ).scalar() or 0

        return {
            "total_income": income_sum,
            "total_expenses": expense_sum
        }

    def get_budgets_with_spending(self, user_id: int, year: int, month: int) -> List[Dict[str, Any]]:
        month_date = date(year, month, 1)

        budgets = self.db.query(
            Budget,
            Category.name,
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.type == TransactionType.EXPENSE, Transaction.amount),
                        else_=0
                    )
                ), 0
            ).label('spent')
        ).join(
            Category, Budget.category_id == Category.id
        ).outerjoin(
            Transaction,
            and_(
                Transaction.category_id == Budget.category_id,
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            )
        ).filter(
            and_(
                Budget.user_id == user_id,
                Budget.month == month_date
            )
        ).group_by(Budget.id, Category.name).all()

        result = []
        for budget, category_name, spent in budgets:
            result.append({
                "category": category_name,
                "spent": int(spent),
                "limit": budget.amount,
                "percentage": round((spent / budget.amount) * 100, 2) if budget.amount > 0 else 0
            })

        return result

    def get_recent_transactions(self, user_id: int, limit: int = 5, year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self.db.query(
            Transaction,
            Category.name.label('category_name')
        ).join(
            Category, Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user_id
        )

        # Add month/year filtering if provided
        if year is not None and month is not None:
            query = query.filter(
                and_(
                    extract('year', Transaction.created_at) == year,
                    extract('month', Transaction.created_at) == month
                )
            )

        transactions = query.order_by(
            Transaction.created_at.desc()
        ).limit(limit).all()

        result = []
        for transaction, category_name in transactions:
            result.append({
                "id": transaction.id,
                "amount": transaction.amount,
                "type": transaction.type.value,
                "category": category_name,
                "date": transaction.created_at.date()
            })

        return result

    def get_top_expenses(self, user_id: int, year: int, month: int, limit: int = 3) -> List[Dict[str, Any]]:
        expense_query = self.db.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(
            Transaction, Transaction.category_id == Category.id
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                extract('year', Transaction.created_at) == year,
                extract('month', Transaction.created_at) == month
            )
        ).group_by(
            Category.name
        ).order_by(
            func.sum(Transaction.amount).desc()
        ).limit(limit).all()

        total_expenses = sum(amount for _, amount in expense_query)

        result = []
        for category_name, amount in expense_query:
            result.append({
                "category": category_name,
                "amount": amount,
                "percentage": round((amount / total_expenses) * 100, 2) if total_expenses > 0 else 0
            })

        return result
