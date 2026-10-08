from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine
from .routers.carts import router
from .routers.settings import router as settings_router
from .routers.admin import router as admin_router, login_router as admin_login_router
from fastapi.middleware.cors import CORSMiddleware

# Ensure tables exist in Neon when the server starts, not on import,
# so the tests can import the app without connecting to a database
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

# Create the FastAPI app instance
app = FastAPI(title="Move-In Cart API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://movein-cart-management.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(settings_router)
app.include_router(admin_login_router)
app.include_router(admin_router)
