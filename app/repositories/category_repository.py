from typing import Optional
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_by_user_id_and_name(self, user_id: int, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.user_id == user_id, Category.name == name).first()
