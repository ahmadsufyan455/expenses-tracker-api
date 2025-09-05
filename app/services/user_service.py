from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UnauthorizedError
from app.utils.validation import is_password_length_valid


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        user_dict = user_data.model_dump(exclude_unset=True)

        if 'email' in user_dict:
            if self.repository.email_exists(user_dict['email'], exclude_user_id=user_id):
                raise ConflictError("Email already exists")

        try:
            return self.repository.update(user, user_dict)
        except IntegrityError:
            raise ConflictError("Email already exists")

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError("current password is incorrect")

        if not is_password_length_valid(new_password):
            raise ValidationError("New password must be at least 8 characters long")

        hashed_password = get_password_hash(new_password)
        password_dict = {'hashed_password': hashed_password}
        self.repository.update(user, password_dict)

        return True

    def delete_user(self, user_id: int) -> bool:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        self.repository.delete(user_id)

        return True
