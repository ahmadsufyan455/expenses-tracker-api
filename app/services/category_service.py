from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.constants.messages import CategoryMessages
from app.repositories.transaction_repository import TransactionRepository


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)
        self.transaction_repository = TransactionRepository(db)

    def get_user_categories(self, user_id: int):
        return self.repository.get_category_with_usage_count(user_id)

    def create_category(self, user_id: int, category_data: CategoryCreate):
        category = self.repository.get_by_user_id_and_name(user_id, category_data.name)

        if category:
            raise ConflictError(CategoryMessages.ALREADY_EXISTS.value)

        category_dict = category_data.model_dump()
        category_dict.update({
            'user_id': user_id
        })

        created_category = self.repository.create(category_dict)
        return self.repository.get_single_category_with_usage_count(created_category.id, user_id)

    def update_category(self, category_id: int, user_id: int, category_data: CategoryUpdate):
        category = self.repository.get_by_id(category_id)

        if not category:
            raise NotFoundError(CategoryMessages.NOT_FOUND.value)

        if category.user_id != user_id:
            raise NotFoundError(CategoryMessages.NOT_FOUND.value)

        category_exists = self.repository.get_by_user_id_and_name(user_id, category_data.name)
        if category_exists:
            raise ConflictError(CategoryMessages.ALREADY_EXISTS.value)

        self.repository.update(category, category_data.model_dump())
        return self.repository.get_single_category_with_usage_count(category_id, user_id)

    def delete_category(self, category_id: int, user_id: int) -> bool:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError(CategoryMessages.NOT_FOUND.value)

        if category.user_id != user_id:
            raise NotFoundError(CategoryMessages.NOT_FOUND.value)

        # Check if category has transactions
        transaction_count = self.transaction_repository.count_by_category_id(category_id)
        if transaction_count > 0:
            raise ConflictError(CategoryMessages.CANNOT_DELETE_HAS_TRANSACTIONS.value)

        return self.repository.delete(category_id)
