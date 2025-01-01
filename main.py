from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from database import Base, engine
from routers import auth
from routes import categories, listings, cart, reviews, orders
from logging_config import log_request_middleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.middleware("http")(log_request_middleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert validation errors to 400 Bad Request"""
    errors = exc.errors()

    # Handle missing fields
    missing_fields = [err for err in errors if err["type"] == "missing"]
    if missing_fields:
        # Return only the first missing field
        field = missing_fields[0]["loc"][-1]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Field '{field}' is required"},
        )

    # Handle empty fields and other validation errors
    if errors:
        # Get the first error
        error = errors[0]
        if "msg" in error:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": error["msg"]},
            )

    # Fallback error
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


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
