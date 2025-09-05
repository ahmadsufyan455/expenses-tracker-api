from fastapi import APIRouter, status

from app.api.v1 import router
from app.core.dependencies import UserServiceDep, CurrentUserDep
from app.core.responses import SuccessResponse
from app.schemas.user import PasswordChange, UserResponse, UserUpdate

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(
    user_service: UserServiceDep,
    current_user: CurrentUserDep
) -> SuccessResponse:
    user = user_service.get_user_by_id(current_user["user_id"])
    user_response = UserResponse.model_validate(user)
    return SuccessResponse(message="Profile fetched successfully", data=user_response)


@router.put("/", status_code=status.HTTP_200_OK)
async def update_user(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
    user_data: UserUpdate
) -> SuccessResponse:
    user = user_service.update_user(current_user["user_id"], user_data)
    user_response = UserResponse.model_validate(user)
    return SuccessResponse(message="Profile updated successfully", data=user_response)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_service: UserServiceDep,
    current_user: CurrentUserDep
):
    user_service.delete_user(current_user["user_id"])


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
    password_data: PasswordChange
) -> SuccessResponse:
    user_service.change_password(current_user["user_id"], password_data.current_password, password_data.new_password)
    return SuccessResponse(message="Password changed successfully")
