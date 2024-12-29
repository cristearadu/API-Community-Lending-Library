from pydantic import BaseModel, EmailStr, validator
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("email")
    def validate_email_length(cls, v):
        # Split email into local part and domain
        local_part, domain = v.split("@")

        if len(local_part) > 64:
            raise ValueError("Email local part cannot exceed 64 characters")

        if len(domain) > 255:
            raise ValueError("Email domain cannot exceed 255 characters")

        if len(v) > 254:
            raise ValueError("Total email length cannot exceed 254 characters")

        return v
