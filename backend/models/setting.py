"""
Settings model for storing application configuration in the database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.models.base import Base


class Setting(Base):
    """
    Settings table for storing key-value configuration.

    This allows dynamic configuration without restarting services.
    Common settings:
    - system_prompt_en: The AI system prompt for English calls
    - model_name: OpenAI model to use (e.g., gpt-4o-mini)
    - temperature: LLM temperature setting
    """
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Setting(key='{self.key}', updated_at='{self.updated_at}')>"
