from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(db, Category)

    def get_by_user_id_and_name(self, user_id: int, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.user_id == user_id, Category.name == name).first()

    def get_category_with_usage_count(self, user_id: int) -> List:
        return self.db.execute(text(
            """
            SELECT
                c.id,
                c.name,
                COALESCE(COUNT(t.id), 0) as usage_count
            FROM categories c
            LEFT JOIN transactions t ON c.id = t.category_id
            WHERE c.user_id = :user_id
            GROUP BY c.id, c.name
            ORDER BY usage_count DESC, id DESC
        """
        ), {"user_id": user_id}).fetchall()

    def get_single_category_with_usage_count(self, category_id: int, user_id: int):
        result = self.db.execute(text(
            """
            SELECT
                c.id,
                c.name,
                COALESCE(COUNT(t.id), 0) as usage_count
            FROM categories c
            LEFT JOIN transactions t ON c.id = t.category_id
            WHERE c.id = :category_id AND c.user_id = :user_id
            GROUP BY c.id, c.name
        """
        ), {"category_id": category_id, "user_id": user_id}).fetchone()
        return result
