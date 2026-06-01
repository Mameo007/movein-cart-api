from datetime import datetime
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