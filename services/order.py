from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.order import Order, OrderItem, OrderStatus
from models.listing import Listing, ListingStatus
from schemas.order import OrderCreate, OrderUpdate
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from decimal import Decimal

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def get_orders(
        self, 
        buyer_id: UUID,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        return self.db.query(Order)\
            .filter(Order.buyer_id == buyer_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    def get_order_by_id(self, order_id: UUID, buyer_id: UUID) -> Optional[Order]:
        return self.db.query(Order).filter(
            and_(
                Order.id == order_id,
                Order.buyer_id == buyer_id
            )
        ).first()

    def create_order(self, order: OrderCreate) -> Order:
        # Calculate total and verify listings
        total_amount = Decimal('0')
        order_items = []

        for item in order.items:
            listing = self.db.query(Listing).filter(
                and_(
                    Listing.id == item.listing_id,
                    Listing.status == ListingStatus.AVAILABLE
                )
            ).first()

            if not listing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Listing {item.listing_id} not available"
                )

            total_amount += listing.price * item.quantity
            order_items.append({
                "listing_id": listing.id,
                "quantity": item.quantity,
                "price_at_time": listing.price
            })

            # Update listing status
            listing.status = ListingStatus.SOLD

        # Create order
        db_order = Order(
            buyer_id=order.buyer_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        self.db.add(db_order)
        self.db.flush()  # Get order ID without committing

        # Create order items
        for item in order_items:
            db_order_item = OrderItem(
                order_id=db_order.id,
                **item
            )
            self.db.add(db_order_item)

        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def update_order_status(
        self, 
        order_id: UUID, 
        status: OrderStatus,
        buyer_id: UUID
    ) -> Optional[Order]:
        db_order = self.get_order_by_id(order_id, buyer_id)
        if not db_order:
            return None

        # Validate status transition
        if not self._is_valid_status_transition(db_order.status, status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status transition"
            )

        db_order.status = status
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def _is_valid_status_transition(self, current: OrderStatus, new: OrderStatus) -> bool:
        # Define valid transitions
        valid_transitions = {
            OrderStatus.PENDING: {OrderStatus.PAID, OrderStatus.CANCELLED},
            OrderStatus.PAID: {OrderStatus.SHIPPED, OrderStatus.REFUNDED},
            OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: {OrderStatus.REFUNDED},
            OrderStatus.CANCELLED: set(),  # No transitions from cancelled
            OrderStatus.REFUNDED: set(),   # No transitions from refunded
        }

        return new in valid_transitions.get(current, set())

    def cancel_order(self, order_id: UUID, buyer_id: UUID) -> Optional[Order]:
        db_order = self.get_order_by_id(order_id, buyer_id)
        if not db_order or db_order.status != OrderStatus.PENDING:
            return None

        # Update order status
        db_order.status = OrderStatus.CANCELLED

        # Return listings to available
        for item in db_order.items:
            item.listing.status = ListingStatus.AVAILABLE

        self.db.commit()
        self.db.refresh(db_order)
        return db_order 