from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from .timezones import utc_now


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

    # Every timestamp is stored as naive UTC. The site's timezone (a Setting)
    # is only applied when a time is typed in or shown.
    # Set in Python rather than by the database, whose clock zone we don't control
    checked_out_at = Column(DateTime, default=utc_now)
    due_at = Column(DateTime)
    returned_at = Column(DateTime, nullable=True)

class Setting(Base):
    """Site-wide key/value settings the admin can change, like the timezone."""
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String)
