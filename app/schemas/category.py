from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }
