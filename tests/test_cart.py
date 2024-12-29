import pytest
from uuid import uuid4
from fastapi import HTTPException
from models.cart import CartItem
from models.listing import Listing, ListingStatus
from schemas.cart import CartItemCreate
from services.cart import CartService


def test_add_to_cart_success(test_db, test_user, test_listing):
    service = CartService(test_db)
    item = CartItemCreate(listing_id=test_listing.id, quantity=1)

    cart_item = service.add_to_cart(test_user.id, item)

    assert cart_item.user_id == test_user.id
    assert cart_item.listing_id == test_listing.id
    assert cart_item.quantity == 1
    assert cart_item.price_at_add == test_listing.price


def test_add_to_cart_insufficient_stock(test_db, test_user, test_listing):
    service = CartService(test_db)
    item = CartItemCreate(
        listing_id=test_listing.id, quantity=test_listing.quantity + 1
    )

    with pytest.raises(ValueError, match="Not enough items in stock"):
        service.add_to_cart(test_user.id, item)


def test_update_cart_item_success(test_db, test_user, test_cart_item):
    service = CartService(test_db)
    updated_item = service.update_cart_item(test_user.id, test_cart_item.id, 2)

    assert updated_item.quantity == 2


def test_process_checkout_success(test_db, test_user, test_cart_item):
    service = CartService(test_db)
    order = service.process_checkout(test_user.id)

    assert order.user_id == test_user.id
    assert len(order.items) == 1
    assert order.items[0].quantity == test_cart_item.quantity

    # Verify cart is cleared
    cart_items = service.get_cart_items(test_user.id)
    assert len(cart_items) == 0

    # Verify listing quantity is updated
    listing = (
        test_db.query(Listing).filter(Listing.id == test_cart_item.listing_id).first()
    )
    assert listing.quantity == test_cart_item.listing.quantity - test_cart_item.quantity


@pytest.fixture
def test_listing(test_db):
    listing = Listing(
        id=uuid4(),
        title="Test Item",
        price=10.00,
        quantity=5,
        status=ListingStatus.ACTIVE,
    )
    test_db.add(listing)
    test_db.commit()
    return listing


@pytest.fixture
def test_cart_item(test_db, test_user, test_listing):
    cart_item = CartItem(
        user_id=test_user.id,
        listing_id=test_listing.id,
        quantity=1,
        price_at_add=test_listing.price,
    )
    test_db.add(cart_item)
    test_db.commit()
    return cart_item
