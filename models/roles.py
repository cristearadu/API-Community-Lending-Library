from enum import Enum
from sqlalchemy import Column, String, ForeignKey, Enum as SQLAlchemyEnum
from database import Base, BaseModel
from sqlalchemy.orm import relationship


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class Role(Base, BaseModel):
    __tablename__ = "roles"

    name = Column(SQLAlchemyEnum(UserRole), unique=True, nullable=False)
    users = relationship("User", back_populates="role")

    def __str__(self):
        return self.name.value
