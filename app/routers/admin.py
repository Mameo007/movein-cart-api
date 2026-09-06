from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session                  # db session type
from ..models import Cart, Session as SessionModel  # ORM model gets the alias
from ..database import get_db
from ..schemas import AdminLogin, TokenResponse, SessionDueUpdate, SessionResponse, ActiveSessionResponse
from ..auth import verify_password, create_access_token, require_admin

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
def get_active_sessions(db: Session = Depends(get_db)):
    """Master list of every cart currently checked out, soonest due first."""
    rows = (
        db.query(SessionModel, Cart.cart_number)
        .join(Cart, Cart.id == SessionModel.cart_id)
        .filter(SessionModel.returned_at == None)
        .order_by(SessionModel.due_at)
        .all()
    )

    # Each row is (session, cart_number) -- merge them into one response object
    return [_to_response(session, cart_number) for session, cart_number in rows]


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

    db_session.due_at = data.due_at
    db.commit()
    db.refresh(db_session)

    cart_number = db.query(Cart.cart_number).filter(Cart.id == db_session.cart_id).scalar()
    return _to_response(db_session, cart_number)
