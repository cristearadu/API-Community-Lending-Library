from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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


@router.post("/register", status_code=status.HTTP_204_NO_CONTENT)
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


@router.post("/login", response_model=Token)
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


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user information."""
    return current_user


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
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
