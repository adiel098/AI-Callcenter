"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


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

    # Application
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    secret_key: str

    # Monitoring
    sentry_dsn: str | None = None

    # Call Settings
    max_concurrent_calls: int = 50
    call_timeout_seconds: int = 300
    max_conversation_turns: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
