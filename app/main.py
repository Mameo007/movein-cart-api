from fastapi import FastAPI
from .database import Base, engine
from .routers.carts import router

# Create the FastAPI app instance
app = FastAPI(title="Move-In Cart API")

# Ensure tables exist in Neon
Base.metadata.create_all(bind=engine)

app.include_router(router)