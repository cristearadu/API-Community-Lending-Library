from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ReviewBase(BaseModel):
    listing_id: UUID
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: UUID
    reviewer_id: UUID

    class Config:
        from_attributes = True
