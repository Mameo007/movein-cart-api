from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import Cart
from ..database import get_db
from ..schemas import CartCreate, CartResponse

router = APIRouter()

# --- API ENDPOINTS ---
@router.get("/api/carts", response_model=list[CartResponse])
def get_all_carts(db: Session = Depends(get_db)):
    """Fetches all carts from the database."""
    return db.query(Cart).all()

@router.post("/api/carts", response_model=CartResponse)
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