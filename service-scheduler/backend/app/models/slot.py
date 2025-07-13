from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Slot(Base):
    __tablename__ = "slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False, index=True)
    max_participants = Column(Integer, default=1, nullable=False)
    current_participants = Column(Integer, default=0, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="valid_time_range"),
        CheckConstraint("current_participants <= max_participants", name="valid_participants"),
    )

    # Relationships
    creator = relationship("User", back_populates="created_slots")
    bookings = relationship("Booking", back_populates="slot", cascade="all, delete-orphan")

    @property
    def available_spots(self) -> int:
        return self.max_participants - self.current_participants

    @property
    def is_full(self) -> bool:
        return self.current_participants >= self.max_participants

    def __repr__(self):
        return f"<Slot(id={self.id}, title={self.title}, start_time={self.start_time})>"
