"""
Conversation history model - stores conversation turns during calls
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base


class SpeakerRole(str, enum.Enum):
    """Speaker role enum"""
    AI = "ai"
    USER = "user"
    SYSTEM = "system"


class ConversationHistory(Base):
    """Conversation history model"""
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"), nullable=False, index=True)

    # Message data
    role = Column(Enum(SpeakerRole), nullable=False)
    message = Column(Text, nullable=False)

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    call = relationship("Call", back_populates="conversation_history")

    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, call_id={self.call_id}, role='{self.role}')>"
