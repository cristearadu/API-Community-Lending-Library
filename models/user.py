from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, BaseModel


class User(Base, BaseModel):
    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role_id = Column(ForeignKey("roles.id"), nullable=False)

    # Relationships
    role = relationship("Role", backref="users")
    listings = relationship("Listing", back_populates="seller")
    cart_items = relationship("CartItem", back_populates="user")
    reviews = relationship("Review", back_populates="reviewer")