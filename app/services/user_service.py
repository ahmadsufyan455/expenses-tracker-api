from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UnauthorizedError
from app.utils.validation import is_password_length_valid
from app.constants.messages import UserMessages
from app.constants.messages import ValidationMessages
from app.constants.messages import AuthMessages


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(AuthMessages.USER_NOT_FOUND.value)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(AuthMessages.USER_NOT_FOUND.value)

        user_dict = user_data.model_dump(exclude_unset=True)

        if 'email' in user_dict:
            if self.repository.email_exists(user_dict['email'], exclude_user_id=user_id):
                raise ConflictError(AuthMessages.ALREADY_EXISTS.value)

        try:
            return self.repository.update(user, user_dict)
        except IntegrityError:
            raise ConflictError(AuthMessages.ALREADY_EXISTS.value)

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(AuthMessages.USER_NOT_FOUND.value)

        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError(UserMessages.INVALID_CURRENT_PASSWORD.value)

        if not is_password_length_valid(new_password):
            raise ValidationError(ValidationMessages.PASSWORD_TOO_SHORT.value)

        hashed_password = get_password_hash(new_password)
        password_dict = {'hashed_password': hashed_password}
        self.repository.update(user, password_dict)

        return True

    def delete_user(self, user_id: int) -> bool:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(AuthMessages.USER_NOT_FOUND.value)
        self.repository.delete(user_id)

        return True
