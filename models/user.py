from sqlalchemy import Column, String, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from database import Base, BaseModel
from models.roles import UserRole


class User(Base, BaseModel):
    __tablename__ = "users"

    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    role_id = Column(ForeignKey("roles.id"), nullable=False)

    # Relationship
    role = relationship("Role", back_populates="users")

    def __str__(self):
        return f"{self.username} ({self.role.name.value})"

    # Relationships
    listings = relationship("Listing", back_populates="seller")
    cart_items = relationship("CartItem", back_populates="user")
    reviews = relationship("Review", back_populates="reviewer")
