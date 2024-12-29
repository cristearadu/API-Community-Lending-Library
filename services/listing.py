from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.listing import Listing, ListingStatus
from models.user import User
from schemas.listing import ListingCreate, ListingUpdate
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

class ListingService:
    def __init__(self, db: Session):
        self.db = db

    def get_listings(
        self, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[UUID] = None,
        status: Optional[ListingStatus] = None
    ) -> List[Listing]:
        query = self.db.query(Listing)
        
        if category_id:
            query = query.filter(Listing.category_id == category_id)
        if status:
            query = query.filter(Listing.status == status)
            
        return query.offset(skip).limit(limit).all()

    def get_listing_by_id(self, listing_id: UUID) -> Optional[Listing]:
        return self.db.query(Listing).filter(Listing.id == listing_id).first()

    def get_user_listings(
        self, 
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Listing]:
        return self.db.query(Listing)\
            .filter(Listing.seller_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def create_listing(self, listing: ListingCreate, seller_id: UUID) -> Listing:
        db_listing = Listing(
            title=listing.title,
            description=listing.description,
            price=listing.price,
            category_id=listing.category_id,
            seller_id=seller_id,
            status=ListingStatus.AVAILABLE
        )
        self.db.add(db_listing)
        self.db.commit()
        self.db.refresh(db_listing)
        return db_listing

    def update_listing(
        self, 
        listing_id: UUID, 
        listing: ListingUpdate, 
        user_id: UUID
    ) -> Optional[Listing]:
        db_listing = self.db.query(Listing).filter(
            and_(
                Listing.id == listing_id,
                Listing.seller_id == user_id
            )
        ).first()

        if not db_listing:
            return None

        for key, value in listing.model_dump(exclude_unset=True).items():
            setattr(db_listing, key, value)

        self.db.commit()
        self.db.refresh(db_listing)
        return db_listing

    def delete_listing(self, listing_id: UUID, user_id: UUID) -> bool:
        result = self.db.query(Listing).filter(
            and_(
                Listing.id == listing_id,
                Listing.seller_id == user_id
            )
        ).delete()
        self.db.commit()
        return result > 0

    def update_listing_status(
        self, 
        listing_id: UUID, 
        status: ListingStatus,
        user_id: UUID
    ) -> Optional[Listing]:
        db_listing = self.db.query(Listing).filter(
            and_(
                Listing.id == listing_id,
                Listing.seller_id == user_id
            )
        ).first()

        if not db_listing:
            return None

        db_listing.status = status
        self.db.commit()
        self.db.refresh(db_listing)
        return db_listing 