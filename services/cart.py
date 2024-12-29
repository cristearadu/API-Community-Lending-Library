from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.cart import CartItem
from models.listing import Listing, ListingStatus
from models.order import Order, OrderItem, OrderStatus
from schemas.cart import CartItemCreate, CartSummary
from decimal import Decimal
from sqlalchemy import and_


class CartService:
    def __init__(self, db: Session):
        self.db = db

    def add_to_cart(self, user_id: UUID, item: CartItemCreate) -> CartItem:
        # Check if listing exists and has enough quantity
        listing = (
            self.db.query(Listing)
            .filter(
                and_(
                    Listing.id == item.listing_id,
                    Listing.status == ListingStatus.ACTIVE,
                )
            )
            .first()
        )

        if not listing:
            raise ValueError("Listing not found or not active")

        if listing.quantity < item.quantity:
            raise ValueError("Not enough items in stock")

        # Check if item already in cart
        existing_item = (
            self.db.query(CartItem)
            .filter(
                and_(
                    CartItem.user_id == user_id, CartItem.listing_id == item.listing_id
                )
            )
            .first()
        )

        if existing_item:
            new_quantity = existing_item.quantity + item.quantity
            if new_quantity > listing.quantity:
                raise ValueError("Not enough items in stock")
            existing_item.quantity = new_quantity
            cart_item = existing_item
        else:
            cart_item = CartItem(
                user_id=user_id,
                listing_id=item.listing_id,
                quantity=item.quantity,
                price_at_add=listing.price,
            )
            self.db.add(cart_item)

        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def get_cart_items(self, user_id: UUID) -> list[CartItem]:
        return self.db.query(CartItem).filter(CartItem.user_id == user_id).all()

    def get_cart_summary(self, user_id: UUID) -> CartSummary:
        items = self.get_cart_items(user_id)
        total = sum(item.price_at_add * item.quantity for item in items)
        return CartSummary(items=items, total=Decimal(total))

    def update_cart_item(self, user_id: UUID, item_id: UUID, quantity: int) -> CartItem:
        cart_item = (
            self.db.query(CartItem)
            .filter(and_(CartItem.id == item_id, CartItem.user_id == user_id))
            .first()
        )

        if not cart_item:
            return None

        listing = (
            self.db.query(Listing).filter(Listing.id == cart_item.listing_id).first()
        )
        if listing.quantity < quantity:
            raise ValueError("Not enough items in stock")

        cart_item.quantity = quantity
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def remove_from_cart(self, user_id: UUID, item_id: UUID) -> bool:
        result = (
            self.db.query(CartItem)
            .filter(and_(CartItem.id == item_id, CartItem.user_id == user_id))
            .delete()
        )
        self.db.commit()
        return result > 0

    def clear_cart(self, user_id: UUID):
        self.db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        self.db.commit()

    def process_checkout(self, user_id: UUID) -> Order:
        cart_items = self.get_cart_items(user_id)
        if not cart_items:
            raise ValueError("Cart is empty")

        # Verify stock and calculate total
        total = Decimal(0)
        order_items = []

        for cart_item in cart_items:
            listing = (
                self.db.query(Listing)
                .filter(Listing.id == cart_item.listing_id)
                .first()
            )

            if not listing or listing.status != ListingStatus.ACTIVE:
                raise ValueError(f"Listing {listing.id} is no longer available")

            if listing.quantity < cart_item.quantity:
                raise ValueError(f"Not enough stock for {listing.title}")

            # Update listing quantity
            listing.quantity -= cart_item.quantity
            if listing.quantity == 0:
                listing.status = ListingStatus.SOLD_OUT

            total += Decimal(cart_item.price_at_add * cart_item.quantity)

            order_items.append(
                OrderItem(
                    listing_id=listing.id,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.price_at_add,
                )
            )

        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total,
            status=OrderStatus.PENDING,
            items=order_items,
        )

        self.db.add(order)
        self.clear_cart(user_id)  # Clear the cart after successful checkout
        self.db.commit()
        self.db.refresh(order)

        return order
