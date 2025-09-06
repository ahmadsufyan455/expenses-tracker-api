from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.config.settings import Settings
from app.core.exceptions import NotFoundError, UnauthorizedError, ConflictError, ValidationError
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, Token as TokenData
from app.models.user import User
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.user import UserCreate
from app.config.settings import settings
from app.utils.validation import is_password_length_valid
from app.constants.messages import AuthMessages
from app.constants.messages import ValidationMessages


class AuthService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        if self.repository.email_exists(user_data.email):
            raise ConflictError(AuthMessages.ALREADY_EXISTS.value)

        if not is_password_length_valid(user_data.password):
            raise ValidationError(ValidationMessages.PASSWORD_TOO_SHORT.value)

        hashed_password = get_password_hash(user_data.password)

        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['hashed_password'] = hashed_password

        try:
            return self.repository.create(user_dict)
        except IntegrityError:
            raise ConflictError(AuthMessages.ALREADY_EXISTS.value)

    def authenticate_user(self, login_data: LoginRequest) -> TokenData:
        user = self.repository.get_by_email(login_data.email)

        if not user:
            raise NotFoundError(AuthMessages.USER_NOT_FOUND.value)

        if not verify_password(login_data.password, user.hashed_password):
            raise UnauthorizedError(AuthMessages.INVALID_PASSWORD.value)

        access_token = create_access_token(
            user_id=user.id,
            email=user.email
        )

        return TokenData(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )
