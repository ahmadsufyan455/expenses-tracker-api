from typing import List
from datetime import datetime, date, timedelta
import calendar
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetUpdate, PredictionType
from app.models.budget import Budget
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.constants.messages import BudgetMessages


class BudgetService:
    def __init__(self, db: Session):
        self.repository = BudgetRepository(db)

    def get_user_budgets(self, user_id: int, skip: int = 0, limit: int = 100, sort_by: str = "created_at", sort_order: str = "desc"):
        """Get user budgets with prediction data when enabled (with pagination)"""
        # Get total count
        total = self.repository.count_by_user_id(user_id)

        # Get paginated budget data
        budget_data = self.repository.get_budgets_with_spending_data(user_id, skip, limit, sort_by, sort_order)

        result = []
        for item in budget_data:
            budget = item['budget']
            total_spent = item['total_spent']

            budget_dict = {
                'id': budget.id,
                'category_id': budget.category_id,
                'amount': budget.amount,
                'start_date': budget.start_date,
                'end_date': budget.end_date,
                'prediction_enabled': budget.prediction_enabled,
                'prediction_type': budget.prediction_type,
                'prediction_days_count': budget.prediction_days_count,
                'prediction': None
            }

            # Calculate prediction if enabled
            if budget.prediction_enabled:
                prediction = self._calculate_prediction(budget, total_spent)
                if prediction:
                    budget_dict['prediction'] = prediction

            result.append(budget_dict)

        return result, total

    def create_budget(self, user_id: int, budget_data: BudgetCreate) -> Budget:
        # Validate prediction settings
        self._validate_prediction_settings(budget_data)

        # Check for overlapping budgets
        if self.repository.check_date_range_overlap(
            user_id, budget_data.category_id, budget_data.start_date, budget_data.end_date
        ):
            raise ConflictError(BudgetMessages.ALREADY_EXISTS.value)

        budget_dict = budget_data.model_dump()
        budget_dict.update({
            'user_id': user_id
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

        # Validate prediction settings if provided
        if budget_data.prediction_enabled is not None:
            self._validate_prediction_settings(budget_data)

        # Check for overlapping budgets if dates are being changed
        update_data = budget_data.model_dump(exclude_unset=True)
        if 'start_date' in update_data or 'end_date' in update_data:
            # Use new dates if provided, otherwise use existing dates
            start_date = update_data.get('start_date', budget.start_date)
            end_date = update_data.get('end_date', budget.end_date)
            category_id = update_data.get('category_id', budget.category_id)

            if self.repository.check_date_range_overlap(
                user_id, category_id, start_date, end_date, exclude_budget_id=budget_id
            ):
                raise ConflictError(BudgetMessages.ALREADY_EXISTS.value)

        try:
            return self.repository.update(budget, update_data)
        except IntegrityError:
            raise ConflictError(BudgetMessages.ALREADY_EXISTS.value)

    def delete_budget(self, budget_id: int, user_id: int) -> bool:
        budget = self.repository.get_by_id(budget_id)
        if not budget or budget.user_id != user_id:
            raise NotFoundError(BudgetMessages.NOT_FOUND.value)

        return self.repository.delete(budget_id)


    def _calculate_prediction(self, budget: Budget, total_spent: int) -> dict:
        """Calculate prediction data for a budget"""
        remaining_budget = budget.amount - total_spent
        today = datetime.now().date()

        # Calculate days remaining in budget period
        if today < budget.start_date:
            # Budget hasn't started yet, use full period
            total_days = (budget.end_date - budget.start_date).days + 1
            days_remaining = total_days
        elif today > budget.end_date:
            # Budget period has ended
            days_remaining = 0
        else:
            # Budget is active, calculate remaining days
            days_remaining = (budget.end_date - today).days + 1

        # Calculate applicable days based on prediction type
        applicable_days = self._get_applicable_days_in_range(budget, today, budget.end_date, days_remaining)

        if applicable_days <= 0:
            daily_allowance = 0
        else:
            daily_allowance = max(0, remaining_budget // applicable_days)

        return {
            'daily_allowance': daily_allowance,
            'remaining_budget': remaining_budget,
            'days_remaining': applicable_days,
            'prediction_type': budget.prediction_type
        }

    def _get_applicable_days_in_range(self, budget: Budget, start_date: date, end_date: date, total_days: int) -> int:
        """Calculate applicable days based on prediction type within date range"""
        if budget.prediction_type == PredictionType.DAILY:
            return total_days
        elif budget.prediction_type == PredictionType.CUSTOM:
            # For custom, use the specified days count, but don't exceed remaining days
            return min(budget.prediction_days_count or total_days, total_days)
        elif budget.prediction_type == PredictionType.WEEKENDS:
            # Count weekend days in the remaining period
            return self._count_days_by_type_in_range(start_date, end_date, [5, 6])  # Sat, Sun
        elif budget.prediction_type == PredictionType.WEEKDAYS:
            # Count weekday days in the remaining period
            return self._count_days_by_type_in_range(start_date, end_date, [0, 1, 2, 3, 4])  # Mon-Fri
        else:
            return total_days

    def _count_days_by_type_in_range(self, start_date: date, end_date: date, target_weekdays: list) -> int:
        """Count specific weekday types in a date range"""
        count = 0
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() in target_weekdays:
                count += 1
            current_date += timedelta(days=1)

        return count

    def _validate_prediction_settings(self, budget_data):
        """Validate prediction configuration"""
        if budget_data.prediction_enabled:
            if not budget_data.prediction_type:
                raise ValidationError(BudgetMessages.PREDICTION_TYPE_REQUIRED.value)

            if (budget_data.prediction_type == PredictionType.CUSTOM and
                budget_data.prediction_days_count and
                    (budget_data.prediction_days_count < 1 or budget_data.prediction_days_count > 31)):
                raise ValidationError(BudgetMessages.PREDICTION_INVALID_CUSTOM_DAYS.value)
