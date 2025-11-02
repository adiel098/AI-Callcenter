"""
Partner model - represents external partners who can transfer leads via API
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import secrets

from .base import Base


class Partner(Base):
    """
    Partner model for API access control.

    Partners are external organizations/users who can submit leads
    to our platform via the secure API endpoint.

    Attributes:
        id: Primary key
        name: Partner organization name
        api_key: Unique API key for authentication (hashed)
        is_active: Whether this partner's access is currently enabled
        rate_limit: Max leads per minute (default 100)
        created_at: When partner was created
        updated_at: When partner was last modified

    Relationships:
        leads: Leads submitted by this partner
    """
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    api_key = Column(String(64), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    rate_limit = Column(Integer, default=100, nullable=False)  # leads per minute
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    leads = relationship("Lead", back_populates="partner")

    @staticmethod
    def generate_api_key():
        """
        Generate a secure random API key.

        Returns:
            str: 64-character hexadecimal API key
        """
        return secrets.token_urlsafe(48)  # Generates ~64 chars

    def __repr__(self):
        return f"<Partner(id={self.id}, name='{self.name}', active={self.is_active})>"
