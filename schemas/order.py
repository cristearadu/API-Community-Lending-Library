from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from models.order import OrderStatus

class OrderItemBase(BaseModel):
    listing_id: UUID
    quantity: Decimal = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: UUID
    price_at_time: Decimal
    order_id: UUID

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    buyer_id: UUID
    total_amount: Decimal = Field(..., gt=0)
    status: OrderStatus = OrderStatus.PENDING

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class OrderResponse(OrderBase):
    id: UUID
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

# For order history and listing
class OrderSummary(BaseModel):
    id: UUID
    total_amount: Decimal
    status: OrderStatus
    created_at: str

    class Config:
        from_attributes = True 