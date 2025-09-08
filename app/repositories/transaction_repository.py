from sqlalchemy.orm import Session, joinedload

from app.models.budget import Budget
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(db, Transaction)

    def get_transaction_with_category(self, user_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(Transaction)\
            .options(joinedload(Transaction.category))\
            .filter(Transaction.user_id == user_id)\
            .order_by(Transaction.id)\
            .offset(skip).limit(limit).all()

    def count_by_user_id(self, user_id: int) -> int:
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).count()
