from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    ForeignKey,
    Text,
    Enum as SQLAEnum,
)
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base, BaseModel


class ListingStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SOLD_OUT = "sold_out"
    DELETED = "deleted"


class Listing(Base, BaseModel):
    __tablename__ = "listings"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    category_id = Column(ForeignKey("categories.id"), nullable=False)
    seller_id = Column(ForeignKey("users.id"), nullable=False)
    status = Column(SQLAEnum(ListingStatus), default=ListingStatus.ACTIVE)

    # Relationships
    category = relationship("Category", back_populates="listings")
    seller = relationship("User", back_populates="listings")
    cart_items = relationship("CartItem", back_populates="listing")
    reviews = relationship("Review", back_populates="listing")
