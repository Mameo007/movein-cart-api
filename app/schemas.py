from datetime import datetime, timezone
from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel, ConfigDict, field_validator
from .timezones import is_valid_timezone


def _mark_utc(dt: datetime):
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

# Stored times are naive UTC. Tagging them on the way out makes the JSON end in
# "Z", so the browser reads them as UTC instead of guessing its own local time.
UTCDateTime = Annotated[datetime, AfterValidator(_mark_utc)]

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
    checked_out_at: UTCDateTime
    due_at: UTCDateTime
    returned_at: UTCDateTime | None

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

class SettingsResponse(BaseModel):
    timezone: str

class TimezoneUpdate(BaseModel):
    timezone: str

    @field_validator("timezone")
    @classmethod
    def must_be_known(cls, value):
        if not is_valid_timezone(value):
            raise ValueError("Unknown timezone")
        return value
