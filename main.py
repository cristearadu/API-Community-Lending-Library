from fastapi import FastAPI
from database import Base, engine
from routers import auth
from routes import categories, listings, cart, reviews, orders

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include all routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(categories.router)
app.include_router(listings.router)
app.include_router(cart.router)
app.include_router(reviews.router)
app.include_router(orders.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Marketplace API"}
