"""
Speech services for ElevenLabs voice management
Note: Twilio handles STT/TTS directly for real-time calls
"""
import elevenlabs
import logging
from typing import Optional

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SpeechService:
    """Service for ElevenLabs voice management"""

    def __init__(self):
        # Initialize ElevenLabs API key
        elevenlabs.set_api_key(settings.elevenlabs_api_key)

    def get_available_voices(self) -> list:
        """
        Get list of available ElevenLabs voices

        Returns:
            List of voice dictionaries
        """
        try:
            voices = elevenlabs.voices()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "labels": getattr(voice, 'labels', {})
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Failed to fetch voices: {str(e)}")
            return []
