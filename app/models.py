from .database import Base
from sqlalchemy import Column, Integer, String


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_number = Column(String, unique=True, index=True)
    status = Column(String, default="AVAILABLE")