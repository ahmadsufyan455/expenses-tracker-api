from typing import Optional, Any, List
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None


class PaginatedResponse(BaseModel):
    message: str
    total: int
    page: int
    per_page: int
    data: List[Any]
