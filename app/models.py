from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.sql import func


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_number = Column(String, unique=True, index=True)
    status = Column(String, default="AVAILABLE")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String)
    room_number = Column(String)

    # Auto-set to current timestamp when the session is created
    checked_out_at = Column(DateTime, server_default=func.now())
    due_at = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)
