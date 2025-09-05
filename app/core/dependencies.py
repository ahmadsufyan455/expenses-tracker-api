from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.services.auth_service import AuthService
from app.services.budget_service import BudgetService
from app.services.category_service import CategoryService
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService
from app.core.security import get_current_user


# Database dependency
DatabaseDep = Annotated[Session, Depends(get_db)]

# User dependency
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

# Service dependencies


def get_budget_service(db: DatabaseDep) -> BudgetService:
    return BudgetService(db)


def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)


def get_transaction_service(db: DatabaseDep) -> TransactionService:
    return TransactionService(db)


def get_auth_service(db: DatabaseDep) -> AuthService:
    return AuthService(db)


def get_category_service(db: DatabaseDep) -> CategoryService:
    return CategoryService(db)


# Typed service dependencies
BudgetServiceDep = Annotated[BudgetService, Depends(get_budget_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
