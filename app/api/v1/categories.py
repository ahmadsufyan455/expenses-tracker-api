from fastapi import APIRouter, status
from app.core.dependencies import CategoryServiceDep, CurrentUserDep
from app.core.responses import SuccessResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.constants.messages import CategoryMessages

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_categories(
    category_service: CategoryServiceDep,
    current_user: CurrentUserDep
) -> SuccessResponse:
    categories = category_service.get_user_categories(current_user["user_id"])
    category_responses = [CategoryResponse.model_validate(category) for category in categories]
    return SuccessResponse(message=CategoryMessages.RETRIEVED_SUCCESS.value, data=category_responses)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_service: CategoryServiceDep,
    current_user: CurrentUserDep,
    category_data: CategoryCreate
) -> SuccessResponse:
    category = category_service.create_category(current_user["user_id"], category_data)
    category_response = CategoryResponse.model_validate(category)
    return SuccessResponse(message=CategoryMessages.CREATED_SUCCESS.value, data=category_response)


@router.put("/{category_id}", status_code=status.HTTP_200_OK)
async def update_category(
    category_service: CategoryServiceDep,
    current_user: CurrentUserDep,
    category_id: int,
    category_data: CategoryUpdate
) -> SuccessResponse:
    category = category_service.update_category(category_id, current_user["user_id"], category_data)
    category_response = CategoryResponse.model_validate(category)
    return SuccessResponse(message=CategoryMessages.UPDATED_SUCCESS.value, data=category_response)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_service: CategoryServiceDep,
    current_user: CurrentUserDep,
    category_id: int
):
    category_service.delete_category(category_id, current_user["user_id"])
