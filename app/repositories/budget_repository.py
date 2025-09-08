from typing import Optional
from sqlalchemy.orm import Session
from datetime import date

from app.models.budget import Budget
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
