"""
Meeting model - represents scheduled meetings
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base


class MeetingStatus(str, enum.Enum):
    """Meeting status enum"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class Meeting(Base):
    """Meeting model"""
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=True, index=True)

    # Meeting details
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    guest_email = Column(String(255), nullable=True)
    calendar_event_id = Column(String(255), nullable=True, unique=True)  # Google Calendar event ID
    duration = Column(Integer, nullable=True, default=30)  # Duration in minutes
    meeting_link = Column(Text, nullable=True)  # Zoom video conference link
    notes = Column(Text, nullable=True)  # Additional notes

    # Status
    status = Column(
        Enum(MeetingStatus),
        default=MeetingStatus.SCHEDULED,
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    lead = relationship("Lead", back_populates="meetings")
    call = relationship("Call", back_populates="meetings")

    def __repr__(self):
        return f"<Meeting(id={self.id}, lead_id={self.lead_id}, scheduled_time='{self.scheduled_time}', status='{self.status}')>"
