from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.base_response import ErrorResponse, SuccessResponse
from db.database import get_db
from db.models import Category
from routers.auth import get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["category"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CategoryRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def get_categories(db: db_dependency, user: user_dependency):
    validate_user(user)
    categories = db.query(Category).filter(
        Category.user_id == user.get("user_id")).all()
    category_responses = [CategoryResponse.model_validate(
        category) for category in categories]
    return SuccessResponse(message="Categories retrieved successfully", data=category_responses)


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def create_category(db: db_dependency, user: user_dependency, request: CategoryRequest):
    validate_user(user)

    category = Category(
        user_id=user.get("user_id"),
        name=request.name,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    category_response = CategoryResponse.model_validate(category)

    return SuccessResponse(message="Category created successfully", data=category_response)


@router.put("/{category_id}/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_category(db: db_dependency, user: user_dependency, category_id: int, request: CategoryRequest):
    validate_user(user)

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ErrorResponse(message="Category not found",
                            status_code=status.HTTP_404_NOT_FOUND)
    category.name = request.name

    db.commit()


@router.delete("/{category_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(db: db_dependency, user: user_dependency, category_id: int):
    validate_user(user)

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise ErrorResponse(message="Category not found",
                            status_code=status.HTTP_404_NOT_FOUND)

    db.delete(category)
    db.commit()


def validate_user(user: user_dependency):
    if user.get("user_id") is None:
        raise ErrorResponse(message="Unauthorized",
                            status_code=status.HTTP_401_UNAUTHORIZED)
