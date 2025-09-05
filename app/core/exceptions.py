from fastapi import HTTPException, status


class BaseError(HTTPException):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        super().__init__(status_code=status_code, detail=message)


class NotFoundError(BaseError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictError(BaseError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class ValidationError(BaseError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UnauthorizedError(BaseError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
