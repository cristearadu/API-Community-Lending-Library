from pydantic import BaseModel, Field, SecretStr, EmailStr, field_validator, ValidationError
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
import re
from typing import ClassVar


class UserCreate(BaseModel):
    username: str = Field(..., example="john_doe")
    email: EmailStr = Field(..., example="john_doe@example.com")
    password: SecretStr = Field(..., example="SecurePass1!")

    # Database session to be used for uniqueness checks
    db_session: ClassVar[Session] = None  # This will be set before validation in the endpoint

    @field_validator("username")
    def validate_username(cls, username):
        # Length Check
        if not (3 <= len(username) <= 30):
            raise ValueError("Username must be between 3 and 30 characters")

        # Only alphanumeric characters and underscores
        if not re.match(r"^\w+$", username):  # \w matches [a-zA-Z0-9_]
            raise ValueError("Username can only contain letters, numbers, and underscores")

        # Database uniqueness check for username
        if cls.db_session:
            existing_user = cls.db_session.query(User).filter(User.username == username).first()
            if existing_user:
                raise ValueError("Username already taken")

        return username

    @field_validator("email")
    def validate_email(cls, email):
        # Basic Email Pattern Check
        email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email address")

        # Database uniqueness check for email
        if cls.db_session:
            existing_user = cls.db_session.query(User).filter(User.email == email).first()
            if existing_user:
                raise ValueError("Email already registered")

        return email

    @field_validator("password")
    def validate_password(cls, password: SecretStr):
        password_str = password.get_secret_value()

        # Length Check
        if len(password_str) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Uppercase Letter Check
        if not re.search(r"[A-Z]", password_str):
            raise ValueError("Password must contain at least one uppercase letter")

        # Lowercase Letter Check
        if not re.search(r"[a-z]", password_str):
            raise ValueError("Password must contain at least one lowercase letter")

        # Digit Check
        if not re.search(r"\d", password_str):
            raise ValueError("Password must contain at least one digit")

        # Special Character Check
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password_str):
            raise ValueError("Password must contain at least one special character")

        return password


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True
