from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session                  # db session type
from ..models import Cart, Session as SessionModel  # ORM model gets the alias
from ..database import get_db
from ..schemas import CartResponse, SessionCreate, SessionResponse
from datetime import datetime

router = APIRouter()

# Carts are created, retired and taken out of service from the admin router.
# This one only holds what a resident at the desk needs: list, checkout, return.

def close_session(db_cart, active_session):
    """Marks a session returned and frees its cart. Shared with the admin
    force-return so both paths end a session the same way."""
    active_session.returned_at = datetime.now()
    db_cart.status = "AVAILABLE"

# --- API ENDPOINTS ---

# GET
@router.get("/api/carts", response_model=list[CartResponse])
def get_all_carts(db: Session = Depends(get_db)):
    """Fetches all carts from the database."""
    return db.query(Cart).all()


# CHECKOUT
@router.post("/api/carts/{cart_id}/checkout", response_model=SessionResponse)
def checkout_cart(cart_id: int, data: SessionCreate, db: Session = Depends(get_db)):

    # data is a Pydantic object -- validated JSON from the frontend
    # Use its fields to build a SQLAlchemy object


    # 1. Check if the cart exists, if not, raise a 404 error
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not db_cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # 2. Check if the cart is already checked out, if so, raiase a 400 error
    if db_cart.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail="Cart is already checked out")
    

    new_session = SessionModel(

        # from the URL
        cart_id=cart_id,            

        # from the Pydantic object
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        room_number=data.room_number,
        due_at=data.due_at,            
    )

    # Update the cart's status to "IN_USE"
    db_cart.status = "IN_USE"

    # SQLAlcehmy takes it from here
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

# RETURN
@router.post("/api/carts/{cart_id}/return")
def return_cart(cart_id: int, db: Session = Depends(get_db)):

    # 1. Check if the cart exists, if not, raise a 404 error
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()

    if not db_cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # 2. Only a checked-out cart can be returned (not AVAILABLE or MAINTENANCE)
    if db_cart.status != "IN_USE":
        raise HTTPException(status_code=400, detail="Cart is not currently checked out")
    
    # 3. Find the active session for this cart (the one with returned_at == None)
    active_session = db.query(SessionModel).filter(
        SessionModel.cart_id == db_cart.id, 
        SessionModel.returned_at == None).first()

    if not active_session:
        raise HTTPException(status_code=400, detail="No Active Session Found fo this Cart")
    
    # 4. Set the session's returned_at to now and free the cart
    close_session(db_cart, active_session)

    db.commit()
    db.refresh(db_cart)
    return db_cart
    