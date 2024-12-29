from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class CategoryResponse(CategoryBase):
    id: UUID
    subcategories: List["CategoryResponse"] = []

    class Config:
        from_attributes = True
