from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.review import Review
from models.order import Order, OrderStatus
from schemas.review import ReviewCreate, ReviewUpdate
from fastapi import HTTPException, status


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create_review(self, user_id: UUID, review_data: ReviewCreate) -> Review:
        # Verify user has purchased the item
        order = (
            self.db.query(Order)
            .filter(
                and_(Order.user_id == user_id, Order.status == OrderStatus.COMPLETED)
            )
            .join(Order.items)
            .filter(Order.items.any(listing_id=review_data.listing_id))
            .first()
        )

        if not order:
            raise ValueError("You can only review items you have purchased")

        # Check if user already reviewed this listing
        existing_review = (
            self.db.query(Review)
            .filter(
                and_(
                    Review.listing_id == review_data.listing_id,
                    Review.reviewer_id == user_id,
                )
            )
            .first()
        )

        if existing_review:
            raise ValueError("You have already reviewed this item")

        review = Review(
            listing_id=review_data.listing_id,
            reviewer_id=user_id,
            rating=review_data.rating,
            comment=review_data.comment,
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_listing_reviews(
        self, listing_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Review]:
        return (
            self.db.query(Review)
            .filter(Review.listing_id == listing_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_review(
        self, review_id: UUID, user_id: UUID, review_data: ReviewUpdate
    ) -> Review:
        review = (
            self.db.query(Review)
            .filter(and_(Review.id == review_id, Review.reviewer_id == user_id))
            .first()
        )

        if not review:
            return None

        if review_data.rating is not None:
            review.rating = review_data.rating
        if review_data.comment is not None:
            review.comment = review_data.comment

        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, review_id: UUID, user_id: UUID) -> bool:
        result = (
            self.db.query(Review)
            .filter(and_(Review.id == review_id, Review.reviewer_id == user_id))
            .delete()
        )
        self.db.commit()
        return result > 0
