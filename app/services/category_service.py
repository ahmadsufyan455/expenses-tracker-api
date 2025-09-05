from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)

    def get_user_categories(self, user_id: int):
        return self.repository.get_by_user_id(user_id)

    def create_category(self, user_id: int, category_data: CategoryCreate) -> Category:
        category = self.repository.get_by_user_id_and_name(user_id, category_data.name)

        if category:
            raise ConflictError("Category already exists")

        category_dict = category_data.model_dump()
        category_dict.update({
            'user_id': user_id
        })

        return self.repository.create(category_dict)

    def update_category(self, category_id: int, user_id: int, category_data: CategoryUpdate) -> Category:
        category = self.repository.get_by_id(category_id)

        if not category:
            raise NotFoundError("Category not found")

        if category.user_id != user_id:
            raise NotFoundError("Category not found")

        category_exists = self.repository.get_by_user_id_and_name(user_id, category_data.name)
        if category_exists:
            raise ConflictError("Category already exists")

        return self.repository.update(category, category_data.model_dump())

    def delete_category(self, category_id: int, user_id: int) -> bool:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")

        if category.user_id != user_id:
            raise NotFoundError("Category not found")

        return self.repository.delete(category_id)
