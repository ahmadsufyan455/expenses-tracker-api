from datetime import datetime, date

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.exceptions import NotFoundError, ValidationError
from app.models.transaction import Transaction, TransactionType
from app.repositories.budget_repository import BudgetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.constants.messages import CategoryMessages, TransactionMessages


class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)
        self.budget_repository = BudgetRepository(db)
        self.category_repository = CategoryRepository(db)

    def get_user_transactions_with_category(self, user_id: int, skip: int = 0, limit: int = 100, sort_by: str = "created_at", sort_order: str = "desc"):
        # Get total count
        total = self.repository.count_by_user_id(user_id)

        # Get paginated transactions
        transactions = self.repository.get_transaction_with_category(
            user_id=user_id, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order)

        return transactions, total

    def create_transaction(self, user_id: int, transaction_data: TransactionCreate) -> Transaction:
        # Check if category exists before creating the transaction
        category = self.category_repository.get_by_id(transaction_data.category_id)
        if not category:
            raise NotFoundError(CategoryMessages.NOT_FOUND.value)
        # Enforce strict validation for EXPENSE transactions
        if transaction_data.type == TransactionType.EXPENSE:
            transaction_date = datetime.now().date()
            budget = self._require_budget_for_date(user_id, transaction_data.category_id, transaction_date)

            # Check remaining budget and prevent overspending
            self._validate_budget_limit(budget, user_id, transaction_data.category_id, transaction_data.amount)

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

        # Validate budget limits for expense transactions
        effective_is_expense = effective_type == TransactionType.EXPENSE

        if effective_is_expense:
            # For expense transactions, validate that the new amount doesn't exceed budget
            transaction_date = datetime.now().date()
            budget = self._require_budget_for_date(user_id, effective_category_id, transaction_date)

            # Calculate what the total spent would be after this update
            current_spent = self._get_budget_period_spending(budget, user_id, effective_category_id, exclude_transaction_id=transaction_id)
            new_total_spent = current_spent + effective_amount

            if new_total_spent > budget.amount:
                raise ValidationError(TransactionMessages.EXCEEDED_LIMIT.value)

        return self.repository.update(transaction, update_data)

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError(TransactionMessages.NOT_FOUND.value)

        if transaction.user_id != user_id:
            raise NotFoundError(TransactionMessages.NOT_FOUND.value)

        return self.repository.delete(transaction_id)

    def _require_budget_for_date(self, user_id: int, category_id: int, transaction_date: date):
        """Find budget that covers the transaction date"""
        budget = self.budget_repository.get_budget_for_transaction_date(user_id, category_id, transaction_date)
        if not budget:
            raise ValidationError(TransactionMessages.INVALID_BUDGET_NOT_FOUND.value)
        return budget

    def _validate_budget_limit(self, budget, user_id: int, category_id: int, amount: int):
        """Validate that adding this expense amount won't exceed the budget limit"""
        current_spent = self._get_budget_period_spending(budget, user_id, category_id)
        new_total_spent = current_spent + amount

        if new_total_spent > budget.amount:
            raise ValidationError(TransactionMessages.EXCEEDED_LIMIT.value)

    def _get_budget_period_spending(self, budget, user_id: int, category_id: int, exclude_transaction_id=None):
        """Calculate total spending for a category within the budget period"""
        query = self.repository.db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.type == TransactionType.EXPENSE,
            func.date(Transaction.created_at) >= budget.start_date,
            func.date(Transaction.created_at) <= budget.end_date
        )

        # Exclude specific transaction if updating
        if exclude_transaction_id:
            query = query.filter(Transaction.id != exclude_transaction_id)

        result = query.scalar()
        return int(result) if result else 0
