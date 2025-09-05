from typing import List
from sqlalchemy.orm import Session
from app.core.exceptions import NotFoundError
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.models.transaction import Transaction


class TransactionService:
    def __init__(self, db: Session):
        self.repository = TransactionRepository(db)

    def get_user_transactions(self, user_id: int) -> List[Transaction]:
        return self.repository.get_by_user_id(user_id)

    def create_transaction(self, user_id: int, transaction_data: TransactionCreate) -> Transaction:
        transaction_dict = transaction_data.model_dump()
        transaction_dict.update({
            'user_id': user_id
        })
        return self.repository.create(transaction_dict)

    def update_transaction(self, transaction_id: int, user_id: int, transaction_data: TransactionUpdate) -> Transaction:
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")

        if transaction.user_id != user_id:
            raise NotFoundError("Transaction not found")

        return self.repository.update(transaction, transaction_data.model_dump())

    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        transaction = self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundError("Transaction not found")

        if transaction.user_id != user_id:
            raise NotFoundError("Transaction not found")

        return self.repository.delete(transaction_id)
