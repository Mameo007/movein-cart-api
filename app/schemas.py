from pydantic import BaseModel, ConfigDict

class CartCreate(BaseModel):
    cart_number: str

class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cart_number: str
    status: str