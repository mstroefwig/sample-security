from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class SlotBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    max_participants: int = Field(default=1, ge=1, le=100)


class SlotCreate(SlotBase):
    pass


class SlotUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_participants: Optional[int] = Field(None, ge=1, le=100)
    is_available: Optional[bool] = None


class SlotResponse(SlotBase):
    id: UUID
    is_available: bool
    current_participants: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    available_spots: int
    is_full: bool

    model_config = ConfigDict(from_attributes=True)


class SlotWithCreator(SlotResponse):
    creator: "UserResponse"

    model_config = ConfigDict(from_attributes=True)


# Import here to avoid circular imports
from app.schemas.user import UserResponse
SlotWithCreator.model_rebuild()
