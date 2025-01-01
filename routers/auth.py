from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Annotated
from jose import JWTError, jwt

from database import get_db
from schemas.user import UserCreate, UserResponse, LoginUser, Token, UserDelete
from services.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    oauth2_scheme,
)

from models.user import User
from models.roles import Role, UserRole
from config import settings

router = APIRouter()


@router.post(
    "/register",
    response_model=None,
    status_code=204,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={
        204: {"description": "User successfully registered"},
        400: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "examples": {
                        "username_exists": {
                            "value": {"detail": "Username already registered"}
                        },
                        "email_exists": {
                            "value": {"detail": "Email already registered"}
                        },
                        "invalid_username": {
                            "value": {
                                "detail": "Username must be between 3 and 32 characters"
                            }
                        },
                        "invalid_email": {"value": {"detail": "Invalid email format"}},
                        "invalid_password": {
                            "value": {
                                "detail": "Password must be at least 8 characters long"
                            }
                        },
                    }
                }
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {"detail": "Admin registration is not allowed"}
                }
            },
        },
    },
)
async def register(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    """Register a new user."""
    # Check if username exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Get or create role
    db_role = db.query(Role).filter(Role.name == user.role).first()
    if not db_role:
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot register as admin",
            )
        db_role = Role(name=user.role)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=db_role,
    )
    db.add(db_user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/login",
    response_model=Token,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={
        200: {
            "description": "Successful Login",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "empty_username": {
                            "value": {"detail": "Field 'username' cannot be empty"}
                        },
                        "empty_password": {
                            "value": {"detail": "Field 'password' cannot be empty"}
                        },
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect username or password"}
                }
            },
        },
    },
)
async def login(
    form_data: LoginUser,
    db: Annotated[Session, Depends(get_db)],
):
    """Login user and return JWT token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/users/me",
    response_model=UserResponse,
    responses={
        200: {
            "description": "Return current user details",
            "content": {
                "application/json": {
                    "example": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "username": "string",
                        "email": "string",
                        "role": "buyer",
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "examples": {
                        "not_authenticated": {"value": {"detail": "Not authenticated"}},
                        "invalid_token": {
                            "value": {"detail": "Could not validate credentials"}
                        },
                        "expired_token": {"value": {"detail": "Token has expired"}},
                    }
                }
            },
        },
    },
)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user information."""
    return current_user


@router.delete(
    "/users/me",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    response_model_exclude_unset=True,
    response_model_exclude_none=True,
    responses={
        204: {"description": "User successfully deleted"},
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Field 'password' cannot be empty"}
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_password": {"value": {"detail": "Invalid password"}},
                        "not_authenticated": {"value": {"detail": "Not authenticated"}},
                    }
                }
            },
        },
        404: {
            "description": "Not Found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        },
    },
)
async def delete_user(
    password_data: UserDelete,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        # Decode token first
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Check if user exists
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Verify password using existing authenticate_user function
    authenticated_user = authenticate_user(db, user.username, password_data.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    # Delete user
    db.delete(user)
    db.commit()

    return None
