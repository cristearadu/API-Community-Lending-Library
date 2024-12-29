from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Numeric, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database import Base, BaseModel

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class Order(Base, BaseModel):
    __tablename__ = "orders"

    buyer_id = Column(ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLAlchemyEnum(OrderStatus), default=OrderStatus.PENDING)

    # Relationships
    buyer = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base, BaseModel):
    __tablename__ = "order_items"

    order_id = Column(ForeignKey("orders.id"), nullable=False)
    listing_id = Column(ForeignKey("listings.id"), nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    price_at_time = Column(Numeric(10, 2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")
    listing = relationship("Listing") 