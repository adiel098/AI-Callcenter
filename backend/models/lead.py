"""
Lead model - represents potential clients to call
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base import Base


class LeadStatus(str, enum.Enum):
    """Lead status enum"""
    PENDING = "pending"
    QUEUED = "queued"
    CALLING = "calling"
    CONTACTED = "contacted"
    MEETING_SCHEDULED = "meeting_scheduled"
    NOT_INTERESTED = "not_interested"
    NO_ANSWER = "no_answer"
    FAILED = "failed"


class Lead(Base):
    """Lead model"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True)
    country_code = Column(String(10), nullable=True)  # e.g., +972, +1
    language = Column(String(10), nullable=True)  # e.g., he, en, fr
    status = Column(
        Enum(LeadStatus),
        default=LeadStatus.PENDING,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    calls = relationship("Call", back_populates="lead", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lead(id={self.id}, name='{self.name}', phone='{self.phone}', status='{self.status}')>"
