from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from passlib.context import CryptContext
from tests.utils.auth import create_access_token
from config import settings
from database import get_db
from models.user import User
from models.roles import Role, UserRole
from schemas.user import UserCreate, UserResponse, LoginUser, Token

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


@router.post("/login")
async def login(user_data: LoginUser, db: Session = Depends(get_db)):
    LoginUser.db = db
    try:
        user = authenticate_user(db, user_data.username, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.name},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        delattr(LoginUser, "db")


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot register as admin"
        )
    
    db_role = db.query(Role).filter(Role.name == user.role).first()
    if not db_role:
        db_role = Role(name=user.role)
        db.add(db_role)
        db.commit()

    hashed_password = pwd_context.hash(user.password.get_secret_value())
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role_id=db_role.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
