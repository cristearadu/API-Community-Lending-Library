import re
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator
from models.user import User
from models.roles import UserRole
from fastapi import HTTPException, status
from enum import Enum


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class UserCreate(BaseModel):
    username: str = Field(example="john_doe")
    email: str = Field(example="john_doe@example.com")
    password: str = Field(xample="SecurePass1!")
    role: str = UserRole.BUYER.value  # Default to BUYER if not specified

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("username")
    def validate_username(cls, username):
        # Length Check
        if not (3 <= len(username) <= 30):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be between 3 and 30 characters",
            )

        # Only alphanumeric characters and underscores
        if not re.match(r"^\w+$", username):  # \w matches [a-zA-Z0-9_]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username can only contain letters, numbers, and underscores",
            )
        return username

    @field_validator("email")
    def validate_email(cls, email):
        # Basic Email Pattern Check
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email address"
            )

        try:
            local_part, domain = email.split("@")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
            )

        # RFC 5321 length limits
        if len(local_part) > 64:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email local part cannot exceed 64 characters",
            )

        if len(domain) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email domain cannot exceed 255 characters",
            )

        if len(email) > 254:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total email length cannot exceed 254 characters",
            )

        return email

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long",
            )
        if not any(c.isupper() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter",
            )
        if not any(c.islower() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter",
            )
        if not any(c.isdigit() for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one digit",
            )
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one special character",
            )
        return password

    @model_validator(mode="before")
    @classmethod
    def validate_unique_fields(cls, data):
        db = data.get("db_session")
        if not db:
            return data

        username = data.get("username")
        email = data.get("email")

        if username and db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        if email and db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        return data

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        try:
            role = UserRole(value.lower())
            return role.value
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role"
            )


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: UserRole

    class Config:
        from_attributes = True

    @field_validator("role", mode="before")
    @classmethod
    def extract_role_name(cls, v):
        if hasattr(v, "name"):
            return v.name
        return v


class LoginUser(BaseModel):
    username: str
    password: str

    @field_validator("username")
    def username_exists(cls, v):
        if not v or len(v.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot be empty",
            )

        db = getattr(cls, "db", None)
        if not db:
            return v

        user = db.query(User).filter(User.username == v).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        return v

    @field_validator("password")
    def password_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be empty",
            )
        return v


class UserDelete(BaseModel):
    password: str

    @field_validator("password")
    def password_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be empty",
            )
        return v
