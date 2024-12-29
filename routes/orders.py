from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from schemas.order import OrderResponse, OrderCreate
from services.order import OrderService
from auth.dependencies import get_current_user, check_admin_role

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all orders for the current user"""
    return OrderService(db).get_user_orders(current_user["id"], skip, limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get specific order details"""
    order = OrderService(db).get_order(order_id, current_user["id"])
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cancel an order"""
    try:
        return OrderService(db).cancel_order(order_id, current_user["id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/all", response_model=List[OrderResponse])
async def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role),
):
    """Admin endpoint to get all orders"""
    return OrderService(db).get_all_orders(skip, limit, status)
