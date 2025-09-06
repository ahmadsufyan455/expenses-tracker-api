from fastapi import APIRouter, status

from app.core.dependencies import AuthServiceDep
from app.core.responses import SuccessResponse
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate, UserResponse
from app.constants.messages import AuthMessages

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    auth_service: AuthServiceDep,
    user_data: UserCreate
) -> SuccessResponse:
    user = auth_service.create_user(user_data)
    user_response = UserResponse.model_validate(user)
    return SuccessResponse(message=AuthMessages.REGISTER_SUCCESS.value, data=user_response)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    auth_service: AuthServiceDep,
    login_data: LoginRequest
) -> SuccessResponse:
    token = auth_service.authenticate_user(login_data)
    return SuccessResponse(message=AuthMessages.LOGIN_SUCCESS.value, data=token)
