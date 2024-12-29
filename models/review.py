from sqlalchemy import Column, ForeignKey, Integer, Text, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base, BaseModel


class Review(Base, BaseModel):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 and rating <= 5", name="check_rating_range"),
    )

    listing_id = Column(ForeignKey("listings.id"), nullable=False)
    reviewer_id = Column(ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)

    # Relationships
    listing = relationship("Listing", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
