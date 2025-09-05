from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def email_exists(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        query = self.db.query(User).filter(User.email == email)
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        return query.first() is not None
