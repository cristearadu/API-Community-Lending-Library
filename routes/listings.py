from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from schemas.listing import ListingCreate, ListingUpdate, ListingResponse
from services.listing import ListingService
from services.auth import get_current_user, check_seller_role
from models.listing import ListingStatus

router = APIRouter(prefix="/listings", tags=["Listings"])


@router.post("/", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing: ListingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_seller_role),
):
    return ListingService(db).create_listing(listing, current_user["id"])


@router.get("/", response_model=List[ListingResponse])
async def get_listings(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    status: Optional[ListingStatus] = None,
    seller_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return ListingService(db).get_listings(
        skip=skip,
        limit=limit,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        status=status,
        seller_id=seller_id,
        search=search,
    )


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(listing_id: UUID, db: Session = Depends(get_db)):
    listing = ListingService(db).get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.put("/{listing_id}", response_model=ListingResponse)
async def update_listing(
    listing_id: UUID,
    listing: ListingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    updated_listing = ListingService(db).update_listing(
        listing_id, listing, current_user["id"]
    )
    if not updated_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return updated_listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if not ListingService(db).delete_listing(listing_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Listing not found")
