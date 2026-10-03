from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session                  # db session type
from ..models import Cart, Session as SessionModel  # ORM model gets the alias
from ..database import get_db
from ..schemas import (
    AdminLogin, TokenResponse, SessionDueUpdate, SessionResponse, ActiveSessionResponse,
    CartCreate, CartResponse, CartStatusUpdate, SettingsResponse, TimezoneUpdate,
)
from ..auth import verify_password, create_access_token, require_admin
from .carts import close_session
from .settings import get_site_timezone, set_site_timezone
from ..timezones import to_utc

# Login is public -- it's how you get a token in the first place
login_router = APIRouter(prefix="/api/admin")

# Everything on this router requires a valid admin token, including any
# route added later, so a new endpoint can't accidentally ship unprotected
router = APIRouter(prefix="/api/admin", dependencies=[Depends(require_admin)])

# --- LOGIN ---

@login_router.post("/login", response_model=TokenResponse)
def admin_login(data: AdminLogin):
    """Trades the shared admin password for a short-lived signed token."""
    if not verify_password(data.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return TokenResponse(access_token=create_access_token())

# --- ADMIN ENDPOINTS ---

def _to_response(session, cart_number):
    """Combines a Session row with its cart's number into one response object."""
    fields = SessionResponse.model_validate(session).model_dump()
    return ActiveSessionResponse(**fields, cart_number=cart_number)

@router.get("/sessions", response_model=list[ActiveSessionResponse])
def get_sessions(
    status: Literal["active", "returned", "all"] = "active",
    db: Session = Depends(get_db),
):
    """Active sessions soonest due first (the master list), or past sessions
    newest first for history."""
    query = db.query(SessionModel, Cart.cart_number).join(Cart, Cart.id == SessionModel.cart_id)

    if status == "active":
        query = query.filter(SessionModel.returned_at == None).order_by(SessionModel.due_at)
    else:
        if status == "returned":
            query = query.filter(SessionModel.returned_at != None)
        query = query.order_by(SessionModel.checked_out_at.desc(), SessionModel.id.desc())

    # Each row is (session, cart_number) -- merge them into one response object
    return [_to_response(session, cart_number) for session, cart_number in query.all()]


@router.patch("/sessions/{session_id}", response_model=ActiveSessionResponse)
def update_session_due_at(session_id: int, data: SessionDueUpdate, db: Session = Depends(get_db)):
    """Extends (or shortens) the due time on an active session."""

    # 1. Check the session exists, if not, raise a 404 error
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. A returned cart is history -- don't let its due time be rewritten
    if db_session.returned_at is not None:
        raise HTTPException(status_code=400, detail="Session is already returned")

    db_session.due_at = to_utc(data.due_at, get_site_timezone(db))
    db.commit()
    db.refresh(db_session)

    cart_number = db.query(Cart.cart_number).filter(Cart.id == db_session.cart_id).scalar()
    return _to_response(db_session, cart_number)


@router.post("/sessions/{session_id}/return", response_model=ActiveSessionResponse)
def force_return_session(session_id: int, db: Session = Depends(get_db)):
    """Ends a session from the admin side, e.g. a cart found abandoned in a hallway."""
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if db_session.returned_at is not None:
        raise HTTPException(status_code=400, detail="Session is already returned")

    db_cart = db.query(Cart).filter(Cart.id == db_session.cart_id).first()
    close_session(db_cart, db_session)
    db.commit()
    db.refresh(db_session)

    return _to_response(db_session, db_cart.cart_number)

# --- CART INVENTORY ---

def _get_cart_or_404(cart_id, db):
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not db_cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return db_cart


@router.post("/carts", response_model=CartResponse)
def create_cart(cart: CartCreate, db: Session = Depends(get_db)):
    """Adds a brand new cart to the fleet."""
    if db.query(Cart).filter(Cart.cart_number == cart.cart_number).first():
        raise HTTPException(status_code=400, detail="Cart number already exists")

    new_cart = Cart(cart_number=cart.cart_number)
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    return new_cart


@router.patch("/carts/{cart_id}", response_model=CartResponse)
def update_cart_status(cart_id: int, data: CartStatusUpdate, db: Session = Depends(get_db)):
    """Takes a cart out of service (MAINTENANCE) or puts it back (AVAILABLE)."""
    db_cart = _get_cart_or_404(cart_id, db)

    # A cart someone is using has to be returned first, or its session would be orphaned
    if db_cart.status == "IN_USE":
        raise HTTPException(status_code=400, detail="Cart is checked out -- return it first")

    db_cart.status = data.status
    db.commit()
    db.refresh(db_cart)
    return db_cart


@router.delete("/carts/{cart_id}", status_code=204)
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    """Removes a cart and its past sessions. Use MAINTENANCE instead to keep the history."""
    db_cart = _get_cart_or_404(cart_id, db)

    if db_cart.status == "IN_USE":
        raise HTTPException(status_code=400, detail="Cart is checked out -- return it first")

    # Sessions point at the cart, so they have to go first or Postgres rejects the delete
    db.query(SessionModel).filter(SessionModel.cart_id == cart_id).delete()
    db.delete(db_cart)
    db.commit()

# --- SETTINGS ---

@router.put("/settings/timezone", response_model=SettingsResponse)
def update_timezone(data: TimezoneUpdate, db: Session = Depends(get_db)):
    """Sets the timezone due times are entered and shown in. Stored times are
    UTC, so switching zones changes how they display, not when carts are due."""
    set_site_timezone(db, data.timezone)
    db.commit()
    return SettingsResponse(timezone=get_site_timezone(db))
