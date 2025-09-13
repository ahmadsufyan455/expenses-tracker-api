from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.transaction import Transaction, TransactionType
from app.repositories.budget_repository import BudgetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.constants.messages import TransactionMessages


class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
        self.budget_repository = BudgetRepository(db)

    def get_user_transactions_with_category(self, user_id: int, skip: int = 0, limit: int = 100, sort_by: str = "created_at", sort_order: str = "desc"):
        # Get total count
        total = self.repository.count_by_user_id(user_id)

        # Get paginated transactions
        transactions = self.repository.get_transaction_with_category(user_id=user_id, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order)

        return transactions, total

    def create_transaction(self, user_id: int, transaction_data: TransactionCreate) -> Transaction:
        # Enforce strict validation and budget deduction for EXPENSE transactions
        if transaction_data.type == TransactionType.EXPENSE:
            month_date = self._month_start_now()
            budget = self._require_budget(user_id, transaction_data.category_id, month_date)

            # Check remaining budget and prevent overspending
            self._deduct_from_budget(budget, transaction_data.amount)

        transaction_dict = transaction_data.model_dump()
        transaction_dict.update({
            'user_id': user_id
        })
        return self.repository.create(transaction_dict)

    def update_transaction(self, transaction_id: int, user_id: int, transaction_data: TransactionUpdate) -> Transaction:
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(TransactionMessages.NOT_FOUND.value)

        if transaction.user_id != user_id:
            raise NotFoundError(TransactionMessages.NOT_FOUND.value)

        # Determine effective values after applying the update (fallback to current values)
        update_data = transaction_data.model_dump(exclude_unset=True)
        effective_type = update_data.get('type', transaction.type)
        effective_category_id = update_data.get('category_id', transaction.category_id)
        effective_amount = update_data.get('amount', transaction.amount)

        month_date = self._month_start_now()

        # Budget adjustments depend on original and effective type/category/amount
        original_is_expense = transaction.type == TransactionType.EXPENSE
        effective_is_expense = effective_type == TransactionType.EXPENSE

        if original_is_expense and effective_is_expense:
            if effective_category_id == transaction.category_id:
                # Same category: adjust by delta
                delta = effective_amount - transaction.amount
                self._handle_expense_to_expense_same_category(user_id, effective_category_id, month_date, delta)
            else:
                # Category changed: refund old, deduct new
                self._handle_expense_to_expense_category_changed(
                    user_id,
                    transaction.category_id,
                    effective_category_id,
                    month_date,
                    transaction.amount,
                    effective_amount,
                )
        elif original_is_expense and not effective_is_expense:
            # Refund the old expense back to its budget
            self._handle_expense_to_non_expense(user_id, transaction.category_id, month_date, transaction.amount)
        elif (not original_is_expense) and effective_is_expense:
            # Newly becoming an expense: require and deduct from budget
            self._handle_non_expense_to_expense(user_id, effective_category_id, month_date, effective_amount)

        return self.repository.update(transaction, update_data)

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(TransactionMessages.NOT_FOUND.value)

        if transaction.user_id != user_id:
            raise NotFoundError(TransactionMessages.NOT_FOUND.value)

        return self.repository.delete(transaction_id)

    @staticmethod
    def _month_start_now():
        return datetime.now().replace(day=1).date()

    def _require_budget(self, user_id: int, category_id: int, month_date):
        budget = self.budget_repository.get_by_user_and_category_and_month(user_id, category_id, month_date)
        if not budget:
            raise ValidationError(TransactionMessages.INVALID_BUDGET_NOT_FOUND.value)
        return budget

    def _deduct_from_budget(self, budget, amount: int):
        if amount > budget.amount:
            raise ValidationError(TransactionMessages.EXCEEDED_LIMIT.value)
        self.budget_repository.update(budget, {"amount": budget.amount - amount})

    def _refund_to_budget(self, budget, amount: int):
        self.budget_repository.update(budget, {"amount": budget.amount + amount})

    def _handle_expense_to_expense_same_category(self, user_id: int, category_id: int, month_date, delta: int):
        if delta == 0:
            return
        budget = self._require_budget(user_id, category_id, month_date)
        if delta > 0:
            self._deduct_from_budget(budget, delta)
        else:
            self._refund_to_budget(budget, -delta)

    def _handle_expense_to_expense_category_changed(
            self,
            user_id: int,
            old_category_id: int,
            new_category_id: int,
            month_date,
            old_amount: int,
            new_amount: int,
    ):
        old_budget = self._require_budget(user_id, old_category_id, month_date)
        self._refund_to_budget(old_budget, old_amount)

        new_budget = self._require_budget(user_id, new_category_id, month_date)
        self._deduct_from_budget(new_budget, new_amount)

    def _handle_expense_to_non_expense(self, user_id: int, category_id: int, month_date, amount: int):
        old_budget = self._require_budget(user_id, category_id, month_date)
        self._refund_to_budget(old_budget, amount)

    def _handle_non_expense_to_expense(self, user_id: int, category_id: int, month_date, amount: int):
        new_budget = self._require_budget(user_id, category_id, month_date)
        self._deduct_from_budget(new_budget, amount)
