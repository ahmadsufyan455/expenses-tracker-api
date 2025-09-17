from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    usage_count: Optional[int] = None

    model_config = {
        "from_attributes": True
    }
