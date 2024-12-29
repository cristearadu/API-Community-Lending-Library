from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
from decimal import Decimal
from models.listing import ListingStatus


class ListingBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    category_id: UUID
    status: Optional[ListingStatus] = ListingStatus.ACTIVE

    @validator("price")
    def validate_price(cls, v):
        return round(v, 2)


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    status: Optional[ListingStatus] = None


class ListingResponse(ListingBase):
    id: UUID
    seller_id: UUID

    class Config:
        from_attributes = True
