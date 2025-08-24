from fastapi import status, Depends
from typing import Annotated
from .base_response import ErrorResponse
from routers.auth import get_current_user


def validate_user(user: Annotated[dict, Depends(get_current_user)]):
    if user.get("user_id") is None:
        raise ErrorResponse(message="Unauthorized",
                            status_code=status.HTTP_401_UNAUTHORIZED)
