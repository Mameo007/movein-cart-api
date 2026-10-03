from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict

class CartCreate(BaseModel):
    cart_number: str

class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cart_number: str
    status: str

class SessionCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    room_number: str
    due_at: datetime

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cart_id: int
    first_name: str
    last_name: str
    phone_number: str
    room_number: str
    checked_out_at: datetime
    due_at: datetime
    returned_at: datetime | None

class AdminLogin(BaseModel):
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SessionDueUpdate(BaseModel):
    due_at: datetime

class ActiveSessionResponse(SessionResponse):
    # The cart's label, so the admin list doesn't just show raw cart ids
    cart_number: str

class CartStatusUpdate(BaseModel):
    # IN_USE is only ever set by a checkout, so the admin can't pick it here
    status: Literal["AVAILABLE", "MAINTENANCE"]
