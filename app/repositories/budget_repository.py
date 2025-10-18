from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, text, case
from datetime import date
from enum import Enum

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from .base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, db: Session):
        super().__init__(db, Budget)

    def _convert_enum_value(self, budget_data: dict):
        for key, value in budget_data.items():
            if isinstance(value, Enum):
                budget_data[key] = value.value.upper()

    def create_budget(self, budget_data: dict):
        self._convert_enum_value(budget_data)

        query = text(
            """
            INSERT INTO budgets (user_id, category_id, amount, start_date, end_date, prediction_enabled, prediction_type, prediction_days_count)
            VALUES (:user_id, :category_id, :amount, :start_date, :end_date, :prediction_enabled, :prediction_type, :prediction_days_count)
            RETURNING *
        """
        )

        result = self.db.execute(query, {**budget_data})

        result_row = result.fetchone()
        self.db.commit()

        result_dict = dict(result_row._mapping)

        return result_dict

    def update_budget(self, budget_id: int, budget_data: dict):
        self._convert_enum_value(budget_data)
        query = text(
            """
            UPDATE budgets
            SET category_id = COALESCE(:category_id, category_id),
                amount = COALESCE(:amount, amount),
                start_date = COALESCE(:start_date, start_date),
                end_date = COALESCE(:end_date, end_date),
                prediction_enabled = COALESCE(:prediction_enabled, prediction_enabled),
                prediction_type = COALESCE(:prediction_type, prediction_type),
                prediction_days_count = COALESCE(:prediction_days_count, prediction_days_count)
            WHERE id = :id
            RETURNING *
        """
        )

        result = self.db.execute(
            query,
            {"id": budget_id, **budget_data},
        )

        updated_row = result.fetchone()
        self.db.commit()

        updated_dict = dict(updated_row._mapping)

        return updated_dict

    def _apply_status_filter(self, query, status: int):
        """
        Apply status filter to query based on date calculations.

        Status values:
        - 1: active (start_date <= today <= end_date)
        - 2: upcoming (start_date > today)
        - 3: expired (end_date < today)
        """
        today = date.today()
        if status == 1:  # active
            query = query.filter(Budget.start_date <= today, Budget.end_date >= today)
        elif status == 2:  # upcoming
            query = query.filter(Budget.start_date > today)
        elif status == 3:  # expired
            query = query.filter(Budget.end_date < today)
        return query

    def get_by_user_and_category_and_date_range(
        self, user_id: int, category_id: int, start_date: date, end_date: date
    ) -> Optional[Budget]:
        return (
            self.db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.start_date == start_date,
                Budget.end_date == end_date,
            )
            .first()
        )

    def check_date_range_overlap(
        self,
        user_id: int,
        category_id: int,
        start_date: date,
        end_date: date,
        exclude_budget_id: Optional[int] = None,
    ) -> bool:
        """Check if the given date range overlaps with existing budgets using raw SQL"""
        exclude_clause = ""
        params = {
            "user_id": user_id,
            "category_id": category_id,
            "start_date": start_date,
            "end_date": end_date,
        }

        if exclude_budget_id:
            exclude_clause = "AND id != :exclude_budget_id"
            params["exclude_budget_id"] = exclude_budget_id

        query = text(
            f"""
            SELECT COUNT(*) as overlap_count
            FROM budgets
            WHERE user_id = :user_id
              AND category_id = :category_id
              {exclude_clause}
              AND (
                (start_date <= :end_date AND end_date >= :start_date)
              )
        """
        )

        result = self.db.execute(query, params)
        overlap_count = result.scalar()
        return overlap_count > 0

    def get_budget_for_transaction_date(
        self, user_id: int, category_id: int, transaction_date: date
    ) -> Optional[Budget]:
        """Find budget that covers the given transaction date using raw SQL"""
        query = text(
            """
            SELECT * FROM budgets
            WHERE user_id = :user_id
              AND category_id = :category_id
              AND start_date <= :transaction_date
              AND end_date >= :transaction_date
            LIMIT 1
        """
        )

        result = self.db.execute(
            query,
            {"user_id": user_id, "category_id": category_id, "transaction_date": transaction_date},
        )

        row = result.fetchone()
        if row:
            return self.db.query(Budget).filter(Budget.id == row.id).first()
        return None

    def count_by_user_id(self, user_id: int, status: int = None) -> int:
        """Count total budgets for a user, optionally filtered by status (calculated from dates)"""
        query = self.db.query(Budget).filter(Budget.user_id == user_id)

        if status is not None:
            query = self._apply_status_filter(query, status)

        return query.count()

    def get_budgets_with_spending_data(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status: int = None,
    ) -> List[dict]:
        """Get budgets for a user with spending data for their date ranges (with pagination and optional status filter)"""
        query = (
            self.db.query(
                Budget, func.coalesce(func.sum(Transaction.amount), 0).label("total_spent")
            )
            .outerjoin(
                Transaction,
                (Budget.user_id == Transaction.user_id)
                & (Budget.category_id == Transaction.category_id)
                & (Transaction.type == TransactionType.EXPENSE)
                & (Transaction.transaction_date >= Budget.start_date)
                & (Transaction.transaction_date <= Budget.end_date),
            )
            .filter(Budget.user_id == user_id)
        )

        # Apply status filter if provided (calculated from dates)
        if status is not None:
            query = self._apply_status_filter(query, status)

        query = query.group_by(Budget.id)

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
            today = date.today()
            status_case = case(
                (Budget.start_date > today, 2), (Budget.end_date < today, 3), else_=1
            )
            if sort_order == "desc":
                query = query.order_by(status_case.desc(), Budget.start_date.desc)
            else:
                query = query.order_by(status_case.asc(), Budget.start_date.asc())
        else:
            # Default fallback to id sorting
            query = query.order_by(Budget.id)

        # Apply pagination
        paginated_results = query.offset(skip).limit(limit).all()

        results = []
        for budget, total_spent in paginated_results:
            results.append(
                {"budget": budget, "total_spent": int(total_spent) if total_spent else 0}
            )

        return results
