from typing import Optional, Any
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None
