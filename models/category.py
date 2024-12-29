from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from uuid import UUID
from database import Base, BaseModel


class Category(Base, BaseModel):
    __tablename__ = "categories"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(ForeignKey("categories.id"), nullable=True)

    # Relationships
    parent = relationship(
        "Category", remote_side="Category.id", backref="subcategories"
    )
    listings = relationship("Listing", back_populates="category")
