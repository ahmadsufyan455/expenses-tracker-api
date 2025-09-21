from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from .base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, db: Session):
        super().__init__(db, Budget)

    def get_by_user_and_category_and_date_range(
        self,
        user_id: int,
        category_id: int,
        start_date: date,
        end_date: date
    ) -> Optional[Budget]:
        return self.db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category_id == category_id,
            Budget.start_date == start_date,
            Budget.end_date == end_date
        ).first()

    def check_date_range_overlap(
        self,
        user_id: int,
        category_id: int,
        start_date: date,
        end_date: date,
        exclude_budget_id: Optional[int] = None
    ) -> bool:
        """Check if the given date range overlaps with existing budgets using raw SQL"""
        exclude_clause = ""
        params = {
            'user_id': user_id,
            'category_id': category_id,
            'start_date': start_date,
            'end_date': end_date
        }

        if exclude_budget_id:
            exclude_clause = "AND id != :exclude_budget_id"
            params['exclude_budget_id'] = exclude_budget_id

        query = text(f"""
            SELECT COUNT(*) as overlap_count
            FROM budgets
            WHERE user_id = :user_id
              AND category_id = :category_id
              {exclude_clause}
              AND (
                (start_date <= :end_date AND end_date >= :start_date)
              )
        """)

        result = self.db.execute(query, params)
        overlap_count = result.scalar()
        return overlap_count > 0

    def get_budget_for_transaction_date(
        self,
        user_id: int,
        category_id: int,
        transaction_date: date
    ) -> Optional[Budget]:
        """Find budget that covers the given transaction date using raw SQL"""
        query = text("""
            SELECT * FROM budgets
            WHERE user_id = :user_id
              AND category_id = :category_id
              AND start_date <= :transaction_date
              AND end_date >= :transaction_date
            LIMIT 1
        """)

        result = self.db.execute(query, {
            'user_id': user_id,
            'category_id': category_id,
            'transaction_date': transaction_date
        })

        row = result.fetchone()
        if row:
            return self.db.query(Budget).filter(Budget.id == row.id).first()
        return None

    def count_by_user_id(self, user_id: int) -> int:
        """Count total budgets for a user"""
        return self.db.query(Budget).filter(Budget.user_id == user_id).count()

    def get_budgets_with_spending_data(self, user_id: int, skip: int = 0, limit: int = 100, sort_by: str = "created_at", sort_order: str = "desc") -> List[dict]:
        """Get budgets for a user with spending data for their date ranges (with pagination)"""
        query = self.db.query(
            Budget,
            func.coalesce(func.sum(Transaction.amount), 0).label('total_spent')
        ).outerjoin(
            Transaction,
            (Budget.user_id == Transaction.user_id) &
            (Budget.category_id == Transaction.category_id) &
            (Transaction.type == TransactionType.EXPENSE) &
            (func.date(Transaction.created_at) >= Budget.start_date) &
            (func.date(Transaction.created_at) <= Budget.end_date)
        ).filter(
            Budget.user_id == user_id
        ).group_by(Budget.id)

        # Apply sorting
        if sort_by == "start_date":
            if sort_order == "desc":
                query = query.order_by(Budget.start_date.desc())
            else:
                query = query.order_by(Budget.start_date.asc())
        elif sort_by == "end_date":
            if sort_order == "desc":
                query = query.order_by(Budget.end_date.desc())
            else:
                query = query.order_by(Budget.end_date.asc())
        elif sort_by == "amount":
            if sort_order == "desc":
                query = query.order_by(Budget.amount.desc())
            else:
                query = query.order_by(Budget.amount.asc())
        elif sort_by == "updated_at":
            if sort_order == "desc":
                query = query.order_by(Budget.updated_at.desc())
            else:
                query = query.order_by(Budget.updated_at.asc())
        elif sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(Budget.created_at.desc())
            else:
                query = query.order_by(Budget.created_at.asc())
        elif sort_by == "status":
            # If same status, sort by start date
            # For active and upcoming: earliest start date first
            # For expired: latest end date first (most recently expired first)
            if sort_order == "desc":
                query = query.order_by(Budget.status.desc())
            else:
                query = query.order_by(Budget.status.asc())
        else:
            # Default fallback to id sorting
            query = query.order_by(Budget.id)

        # Apply pagination
        paginated_results = query.offset(skip).limit(limit).all()

        results = []
        for budget, total_spent in paginated_results:
            results.append({
                'budget': budget,
                'total_spent': int(total_spent) if total_spent else 0
            })

        return results
