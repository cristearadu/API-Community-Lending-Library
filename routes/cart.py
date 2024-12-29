from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartSummary
from services.cart import CartService
from auth.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post(
    "/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED
)
async def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add an item to the user's cart"""
    try:
        return CartService(db).add_to_cart(current_user["id"], item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/items", response_model=List[CartItemResponse])
async def get_cart_items(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Get all items in the user's cart"""
    return CartService(db).get_cart_items(current_user["id"])


@router.get("/summary", response_model=CartSummary)
async def get_cart_summary(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Get a summary of the cart including total price"""
    return CartService(db).get_cart_summary(current_user["id"])


@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: UUID,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update quantity of an item in the cart"""
    try:
        updated_item = CartService(db).update_cart_item(
            current_user["id"], item_id, item.quantity
        )
        if not updated_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return updated_item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Remove an item from the cart"""
    if not CartService(db).remove_from_cart(current_user["id"], item_id):
        raise HTTPException(status_code=404, detail="Cart item not found")


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Clear all items from the cart"""
    CartService(db).clear_cart(current_user["id"])


@router.post("/checkout", status_code=status.HTTP_201_CREATED)
async def checkout(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Process checkout for all items in the cart"""
    try:
        return CartService(db).process_checkout(current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
