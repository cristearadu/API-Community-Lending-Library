
from fastapi import FastAPI, Depends
from routers import auth, items
from database import engine, Base
from models import user, item
from schemas.user import UserResponse
from utils.auth import get_current_user

app = FastAPI()

app.include_router(auth.router)

Base.metadata.create_all(bind=engine)


@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: user.User = Depends(get_current_user)):
    return current_user
