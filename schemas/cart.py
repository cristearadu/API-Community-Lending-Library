from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from decimal import Decimal


class CartItemBase(BaseModel):
    listing_id: UUID
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(CartItemBase):
    id: UUID
    price_at_add: Decimal

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    items: List[CartItemResponse]
    total: Decimal
