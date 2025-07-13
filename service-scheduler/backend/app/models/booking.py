from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("slots.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.ACTIVE, index=True)
    notes = Column(Text)
    booked_at = Column(DateTime(timezone=True), server_default=func.now())
    cancelled_at = Column(DateTime(timezone=True))

    # Constraints
    __table_args__ = (
        UniqueConstraint("slot_id", "user_id", name="unique_slot_user_booking"),
    )

    # Relationships
    slot = relationship("Slot", back_populates="bookings")
    user = relationship("User", back_populates="bookings")

    @property
    def is_active(self) -> bool:
        return self.status == BookingStatus.ACTIVE

    def cancel(self):
        """Cancel this booking."""
        self.status = BookingStatus.CANCELLED
        self.cancelled_at = func.now()

    def __repr__(self):
        return f"<Booking(id={self.id}, slot_id={self.slot_id}, user_id={self.user_id}, status={self.status})>"
