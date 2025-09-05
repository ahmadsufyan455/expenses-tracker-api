from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(db, Transaction)
