"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str

    # Redis
    redis_url: str

    # Twilio
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str

    # OpenAI
    openai_api_key: str

    # ElevenLabs
    elevenlabs_api_key: str

    # Deepgram
    deepgram_api_key: str

    # Google Calendar
    google_calendar_credentials_file: str = "credentials.json"
    google_calendar_token_file: str = "token.json"
    google_calendar_id: str
    google_delegated_user_email: Optional[str] = None  # For Domain-Wide Delegation

    # Zoom (optional - for video conference links)
    zoom_account_id: Optional[str] = None
    zoom_client_id: Optional[str] = None
    zoom_client_secret: Optional[str] = None

    # Application
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    secret_key: str

    # Call Settings
    max_concurrent_calls: int = 50
    call_timeout_seconds: int = 300
    max_conversation_turns: int = 20

    # Monitoring
    sentry_dsn: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create a global settings instance for convenience
settings = get_settings()
