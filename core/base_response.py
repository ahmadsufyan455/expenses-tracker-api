from typing import Optional, Any

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class ErrorResponse(Exception):
    def __init__(self, message: str, error: str = None, status_code: int = 400):
        self.message = message
        self.error = error
        self.status_code = status_code
        super().__init__(self.message)
