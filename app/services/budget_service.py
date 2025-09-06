from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate
from app.models.budget import Budget
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.constants.messages import BudgetMessages


class BudgetService:
    def __init__(self, db: Session):
        self.repository = BudgetRepository(db)

    def get_user_budgets(self, user_id: int) -> List[Budget]:
        return self.repository.get_by_user_id(user_id)

    def create_budget(self, user_id: int, budget_data: BudgetCreate) -> Budget:
        # Parse month
        month_date = self._parse_month(budget_data.month)

        # Check if budget already exists
        existing = self.repository.get_by_user_and_category_and_month(
            user_id, budget_data.category_id, month_date
        )
        if existing:
            raise ConflictError(BudgetMessages.ALREADY_EXISTS.value)

        budget_dict = budget_data.model_dump(exclude={'month'})
        budget_dict.update({
            'user_id': user_id,
            'month': month_date
        })

        try:
            return self.repository.create(budget_dict)
        except IntegrityError:
            raise ConflictError(BudgetMessages.ALREADY_EXISTS.value)

    def update_budget(self, budget_id: int, user_id: int, budget_data: BudgetUpdate) -> Budget:
        budget = self.repository.get_by_id(budget_id)
        if not budget:
            raise NotFoundError(BudgetMessages.NOT_FOUND.value)

        if budget.user_id != user_id:
            raise NotFoundError(BudgetMessages.NOT_FOUND.value)

        update_data = budget_data.model_dump(exclude_unset=True)
        if 'month' in update_data:
            update_data['month'] = self._parse_month(update_data['month'])

        try:
            return self.repository.update(budget, update_data)
        except IntegrityError:
            raise ConflictError(BudgetMessages.ALREADY_EXISTS.value)

    def delete_budget(self, budget_id: int, user_id: int) -> bool:
        budget = self.repository.get_by_id(budget_id)
        if not budget or budget.user_id != user_id:
            raise NotFoundError(BudgetMessages.NOT_FOUND.value)

        return self.repository.delete(budget_id)

    def _parse_month(self, month: str):
        try:
            return datetime.strptime(month, "%Y-%m").replace(day=1).date()
        except ValueError:
            raise ValidationError(BudgetMessages.INVALID_MONTH_FORMAT.value)
