import re
from uuid import UUID
from pydantic import (
    BaseModel,
    Field,
    SecretStr,
    EmailStr,
    field_validator,
    model_validator,
    ValidationError,
)
from models.user import User
from fastapi import HTTPException, status


class UserCreate(BaseModel):
    username: str = Field(..., example="john_doe")
    email: str = Field(..., example="john_doe@example.com")
    password: SecretStr = Field(..., example="SecurePass1!")

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

    @field_validator("password")
    def validate_password(cls, password: SecretStr):
        password_str = password.get_secret_value()

        # Length Check
        if len(password_str) < 8:
            raise HTTPException(
                status_code=400, detail="Password must be at least 8 characters long"
            )

        # Uppercase Letter Check
        if not re.search(r"[A-Z]", password_str):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least one uppercase letter",
            )

        # Lowercase Letter Check
        if not re.search(r"[a-z]", password_str):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least one lowercase letter",
            )

        # Digit Check
        if not re.search(r"\d", password_str):
            raise HTTPException(
                status_code=400, detail="Password must contain at least one digit"
            )

        # Special Character Check
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password_str):
            raise HTTPException(
                status_code=400,
                detail="Password must contain at least one special character",
            )

        return password


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str

    class Config:
        orm_mode = True


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
