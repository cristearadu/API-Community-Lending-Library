from enum import Enum
from sqlalchemy import Column, String, Enum as SQLAEnum
from database import Base, BaseModel


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class Role(Base, BaseModel):
    __tablename__ = "roles"

    name = Column(SQLAEnum(UserRole), unique=True, nullable=False)
    description = Column(String(255))
