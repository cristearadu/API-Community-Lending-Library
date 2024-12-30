from sqlalchemy.orm import Session
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate
from typing import List, Optional
from uuid import UUID


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.db.query(Category).offset(skip).limit(limit).all()

    def get_category_by_id(self, category_id: UUID) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def create_category(self, category: CategoryCreate) -> Category:
        db_category = Category(name=category.name, description=category.description)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update_category(
        self, category_id: UUID, category: CategoryUpdate
    ) -> Optional[Category]:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            return None

        for key, value in category.model_dump(exclude_unset=True).items():
            setattr(db_category, key, value)

        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete_category(self, category_id: UUID) -> bool:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            return False

        self.db.delete(db_category)
        self.db.commit()
        return True
