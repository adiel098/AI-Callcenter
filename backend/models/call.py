"""
Call model - represents phone calls made to leads
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base


class CallOutcome(str, enum.Enum):
    """
    Call outcome enum - simplified to 4 actionable statuses

    INTERESTED: Meeting successfully scheduled
    NOT_INTERESTED: User declined/not interested
    NO_ANSWER: No one answered (technical issue, voicemail, etc.)
    BUSY: User interested but no meeting booked yet (needs follow-up)
    """
    INTERESTED = "interested"
    NOT_INTERESTED = "not_interested"
    NO_ANSWER = "no_answer"
    BUSY = "busy"


class Call(Base):
    """Call model"""
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False, index=True)

    # Twilio data
    twilio_call_sid = Column(String(255), unique=True, index=True)
    recording_url = Column(String(500), nullable=True)

    # Call metadata
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # AI-generated call summary (3-4 sentences)
    duration = Column(Float, nullable=True)  # Duration in seconds
    language = Column(String(10), nullable=True)  # Language used in call
    outcome = Column(
        Enum(CallOutcome),
        default=CallOutcome.NO_ANSWER,  # Default to NO_ANSWER instead of removed IN_PROGRESS
        nullable=False,
        index=True
    )

    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="calls")
    conversation_history = relationship(
        "ConversationHistory",
        back_populates="call",
        cascade="all, delete-orphan"
    )
    meetings = relationship("Meeting", back_populates="call")

    def __repr__(self):
        return f"<Call(id={self.id}, lead_id={self.lead_id}, outcome='{self.outcome}')>"
