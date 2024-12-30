from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from services.review import ReviewService
from services.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new review for a purchased item"""
    try:
        return ReviewService(db).create_review(current_user["id"], review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/listing/{listing_id}", response_model=List[ReviewResponse])
async def get_listing_reviews(
    listing_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all reviews for a specific listing"""
    return ReviewService(db).get_listing_reviews(listing_id, skip, limit)


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update user's own review"""
    updated_review = ReviewService(db).update_review(
        review_id, current_user["id"], review
    )
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete user's own review"""
    if not ReviewService(db).delete_review(review_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Review not found")
