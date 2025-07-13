from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class BookingStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class BookingBase(BaseModel):
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    slot_id: UUID


class BookingUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[BookingStatus] = None


class BookingResponse(BookingBase):
    id: UUID
    slot_id: UUID
    user_id: UUID
    status: BookingStatus
    booked_at: datetime
    cancelled_at: Optional[datetime] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class BookingWithDetails(BookingResponse):
    slot: "SlotResponse"
    user: "UserResponse"

    model_config = ConfigDict(from_attributes=True)


# Import here to avoid circular imports
from app.schemas.slot import SlotResponse
from app.schemas.user import UserResponse
BookingWithDetails.model_rebuild()
