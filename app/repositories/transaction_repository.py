from sqlalchemy.orm import Session, joinedload
from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(db, Transaction)

    def get_transaction_with_category(self, user_id: int, skip: int = 0, limit: int = 100, sort_by: str = "created_at", sort_order: str = "desc"):
        query = self.db.query(Transaction)\
            .options(joinedload(Transaction.category))\
            .filter(Transaction.user_id == user_id)

        # Apply sorting
        if sort_by == "created_at":
            if sort_order == "desc":
                query = query.order_by(Transaction.created_at.desc())
            else:
                query = query.order_by(Transaction.created_at.asc())
        else:
            # Default fallback to id sorting
            query = query.order_by(Transaction.id)

        return query.offset(skip).limit(limit).all()\


    def count_by_user_id(self, user_id: int) -> int:
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).count()

    def count_by_category_id(self, category_id: int) -> int:
        """Count transactions for a specifict category"""
        return self.db.query(Transaction).filter(Transaction.category_id == category_id).count()
