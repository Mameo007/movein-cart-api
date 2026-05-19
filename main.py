import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
from pydantic import BaseModel

# 1. Load the database password
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Setup the Database Engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Define your Database Table (The Cart Model)
class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_number = Column(String, unique=True, index=True)
    status = Column(String, default="AVAILABLE")

# Create the table in Neon automatically if it doesn't exist
Base.metadata.create_all(bind=engine)

# 4. Initialize the Web Server
app = FastAPI(title="Move-In Cart API")

# 5. Define what data we expect from the React Frontend
class CartCreate(BaseModel):
    cart_number: str

class CartResponse(BaseModel):
    id: int
    cart_number: str
    status: str
    
    class Config:
        from_attributes = True

# Helper function to open and close database connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Python Cart API!"}

@app.get("/api/carts", response_model=list[CartResponse])
def get_all_carts(db: Session = Depends(get_db)):
    """Fetches all carts from the database."""
    return db.query(Cart).all()

@app.post("/api/carts", response_model=CartResponse)
def create_cart(cart: CartCreate, db: Session = Depends(get_db)):
    """Adds a brand new cart to the database."""
    db_cart = db.query(Cart).filter(Cart.cart_number == cart.cart_number).first()
    if db_cart:
        raise HTTPException(status_code=400, detail="Cart number already exists")
    
    new_cart = Cart(cart_number=cart.cart_number)
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    return new_cart