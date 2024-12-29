from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from database import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from services.category import CategoryService
from auth.dependencies import get_current_user, check_admin_role

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role),
):
    return CategoryService(db).create_category(category)


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return CategoryService(db).get_categories(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: UUID, db: Session = Depends(get_db)):
    category = CategoryService(db).get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role),
):
    updated_category = CategoryService(db).update_category(category_id, category)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(check_admin_role),
):
    if not CategoryService(db).delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
