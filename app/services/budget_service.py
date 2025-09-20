from typing import List
from datetime import datetime, date
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

    def get_user_budgets(self, user_id: int) -> List[dict]:
        """Get user budgets with prediction data when enabled"""
        budget_data = self.repository.get_budgets_with_spending_data(user_id)

        result = []
        for item in budget_data:
            budget = item['budget']
            total_spent = item['total_spent']

            budget_dict = {
                'id': budget.id,
                'category_id': budget.category_id,
                'amount': budget.amount,
                'month': budget.month,
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

        return result

    def create_budget(self, user_id: int, budget_data: BudgetCreate) -> Budget:
        # Parse month
        month_date = self._parse_month(budget_data.month)

        # Validate prediction settings
        self._validate_prediction_settings(budget_data)

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

        # Validate prediction settings if provided
        if budget_data.prediction_enabled is not None:
            self._validate_prediction_settings(budget_data)

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

    def _calculate_prediction(self, budget: Budget, total_spent: int) -> dict:
        """Calculate prediction data for a budget"""
        remaining_budget = budget.amount - total_spent

        # Get days remaining in the month
        today = datetime.now().date()
        budget_month = budget.month

        # If budget is for current month, calculate days remaining
        if (today.year == budget_month.year and today.month == budget_month.month):
            days_in_month = calendar.monthrange(budget_month.year, budget_month.month)[1]
            days_remaining = days_in_month - today.day + 1
        else:
            # For future months, use full month
            days_in_month = calendar.monthrange(budget_month.year, budget_month.month)[1]
            days_remaining = days_in_month

        # Calculate applicable days based on prediction type
        applicable_days = self._get_applicable_days(budget, days_remaining, budget_month)

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

    def _get_applicable_days(self, budget: Budget, days_remaining: int, budget_month: date) -> int:
        """Calculate applicable days based on prediction type"""
        if budget.prediction_type == PredictionType.DAILY:
            return days_remaining
        elif budget.prediction_type == PredictionType.CUSTOM:
            # For custom, use the specified days count, but don't exceed remaining days
            return min(budget.prediction_days_count or days_remaining, days_remaining)
        elif budget.prediction_type == PredictionType.WEEKENDS:
            # Count weekend days remaining in the month
            return self._count_weekend_days_remaining(budget_month)
        elif budget.prediction_type == PredictionType.WEEKDAYS:
            # Count weekday days remaining in the month
            return self._count_weekday_days_remaining(budget_month)
        else:
            return days_remaining

    def _count_weekend_days_remaining(self, budget_month: date) -> int:
        """Count remaining weekend days (Saturday=5, Sunday=6) in the budget month"""
        today = datetime.now().date()
        if today.year != budget_month.year or today.month != budget_month.month:
            # For future months, count all weekends
            days_in_month = calendar.monthrange(budget_month.year, budget_month.month)[1]
            weekend_count = 0
            for day in range(1, days_in_month + 1):
                weekday = date(budget_month.year, budget_month.month, day).weekday()
                if weekday in [5, 6]:  # Saturday=5, Sunday=6
                    weekend_count += 1
            return weekend_count
        else:
            # For current month, count remaining weekends
            days_in_month = calendar.monthrange(budget_month.year, budget_month.month)[1]
            weekend_count = 0
            for day in range(today.day, days_in_month + 1):
                weekday = date(budget_month.year, budget_month.month, day).weekday()
                if weekday in [5, 6]:  # Saturday=5, Sunday=6
                    weekend_count += 1
            return weekend_count

    def _count_weekday_days_remaining(self, budget_month: date) -> int:
        """Count remaining weekday days (Monday=0 to Friday=4) in the budget month"""
        today = datetime.now().date()
        if today.year != budget_month.year or today.month != budget_month.month:
            # For future months, count all weekdays
            days_in_month = calendar.monthrange(budget_month.year, budget_month.month)[1]
            weekday_count = 0
            for day in range(1, days_in_month + 1):
                weekday = date(budget_month.year, budget_month.month, day).weekday()
                if weekday in [0, 1, 2, 3, 4]:  # Monday=0 to Friday=4
                    weekday_count += 1
            return weekday_count
        else:
            # For current month, count remaining weekdays
            days_in_month = calendar.monthrange(budget_month.year, budget_month.month)[1]
            weekday_count = 0
            for day in range(today.day, days_in_month + 1):
                weekday = date(budget_month.year, budget_month.month, day).weekday()
                if weekday in [0, 1, 2, 3, 4]:  # Monday=0 to Friday=4
                    weekday_count += 1
            return weekday_count

    def _validate_prediction_settings(self, budget_data):
        """Validate prediction configuration"""
        if budget_data.prediction_enabled:
            if not budget_data.prediction_type:
                raise ValidationError(BudgetMessages.PREDICTION_TYPE_REQUIRED.value)

            if (budget_data.prediction_type == PredictionType.CUSTOM and
                budget_data.prediction_days_count and
                    (budget_data.prediction_days_count < 1 or budget_data.prediction_days_count > 31)):
                raise ValidationError(BudgetMessages.PREDICTION_INVALID_CUSTOM_DAYS.value)
