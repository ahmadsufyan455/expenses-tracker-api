from fastapi import APIRouter
from . import auth, budgets, categories, dashboard, transactions, user

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
