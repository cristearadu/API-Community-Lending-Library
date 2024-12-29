from sqlalchemy import Column, ForeignKey, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base, BaseModel


class CartItem(Base, BaseModel):
    __tablename__ = "cart_items"

    user_id = Column(ForeignKey("users.id"), nullable=False)
    listing_id = Column(ForeignKey("listings.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_at_add = Column(Float, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="cart_items")
    listing = relationship("Listing", back_populates="cart_items")
