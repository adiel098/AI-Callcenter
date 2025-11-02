"""
Speech services for STT (Deepgram) and TTS (ElevenLabs)
"""
from deepgram import DeepgramClient
import elevenlabs
from elevenlabs import Voice, VoiceSettings
import httpx
import logging
from typing import Optional, AsyncIterator
import io

from backend.config import get_settings
from backend.utils.language_detector import get_deepgram_language_code, get_voice_for_language

logger = logging.getLogger(__name__)
settings = get_settings()


class SpeechService:
    """Service for speech-to-text and text-to-speech operations"""

    def __init__(self):
        # Initialize Deepgram client (v5 SDK)
        self.deepgram_client = DeepgramClient(api_key=settings.deepgram_api_key)

        # Initialize ElevenLabs API key
        elevenlabs.set_api_key(settings.elevenlabs_api_key)

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> Optional[str]:
        """
        Transcribe audio to text using Deepgram

        Args:
            audio_data: Audio bytes (WAV, MP3, etc.)
            language: Language code (e.g., 'en', 'he')

        Returns:
            Transcribed text or None if failed
        """
        try:
            # Convert language code to Deepgram format
            deepgram_language = get_deepgram_language_code(language)

            # Configure Deepgram options (v5 SDK) - passed as dict
            options = {
                "model": "nova-2",
                "language": deepgram_language,
                "smart_format": True,
                "punctuate": True,
                "diarize": False
            }

            # Create payload (v5 SDK)
            payload = {
                "buffer": audio_data,
            }

            # Transcribe using v5 API
            response = self.deepgram_client.listen.v1.media.transcribe_file(
                payload,
                options
            )

            # Extract transcript (v5 API response structure)
            if response and response.results and response.results.channels:
                transcript = response.results.channels[0].alternatives[0].transcript
                logger.info(f"Transcribed ({language}): {transcript[:100]}...")
                return transcript.strip()

            return None

        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return None

    async def transcribe_audio_streaming(
        self,
        audio_stream: AsyncIterator[bytes],
        language: str = "en"
    ) -> AsyncIterator[str]:
        """
        Transcribe streaming audio in real-time using Deepgram

        NOTE: This is a placeholder for future implementation.
        For production, implement full Deepgram streaming with WebSocket.
        Use transcribe_audio() for batch transcription.

        Args:
            audio_stream: Async iterator of audio chunks
            language: Language code

        Yields:
            Transcribed text segments
        """
        logger.warning("Streaming transcription not implemented - use batch transcription with transcribe_audio()")
        raise NotImplementedError("Streaming transcription requires WebSocket implementation. Use transcribe_audio() instead.")

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs

        Args:
            text: Text to synthesize
            language: Language code
            voice_id: ElevenLabs voice ID (auto-selected if None)

        Returns:
            Audio bytes (MP3) or None if failed
        """
        try:
            # Get appropriate voice for language if not specified
            if not voice_id:
                voice_id = get_voice_for_language(language)

            logger.info(f"Synthesizing speech ({language}): {text[:50]}...")

            # Generate audio using ElevenLabs
            audio_generator = elevenlabs.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2",  # Supports multiple languages
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.0,
                    use_speaker_boost=True
                )
            )

            # Collect audio chunks
            audio_chunks = []
            for chunk in audio_generator:
                if chunk:
                    audio_chunks.append(chunk)

            if audio_chunks:
                audio_data = b''.join(audio_chunks)
                logger.info(f"Generated {len(audio_data)} bytes of audio")
                return audio_data

            return None

        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}")
            return None

    async def synthesize_speech_streaming(
        self,
        text: str,
        language: str = "en",
        voice_id: Optional[str] = None
    ) -> AsyncIterator[bytes]:
        """
        Convert text to speech with streaming output

        Args:
            text: Text to synthesize
            language: Language code
            voice_id: ElevenLabs voice ID

        Yields:
            Audio chunks as they are generated
        """
        try:
            if not voice_id:
                voice_id = get_voice_for_language(language)

            logger.info(f"Streaming speech synthesis ({language}): {text[:50]}...")

            # Stream audio generation
            audio_generator = elevenlabs.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2",
                stream=True
            )

            for chunk in audio_generator:
                if chunk:
                    yield chunk

        except Exception as e:
            logger.error(f"Streaming speech synthesis error: {str(e)}")

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

    async def convert_audio_format(
        self,
        audio_data: bytes,
        source_format: str,
        target_format: str
    ) -> Optional[bytes]:
        """
        Convert audio between formats (placeholder - requires ffmpeg or similar)

        Args:
            audio_data: Source audio bytes
            source_format: Source format (e.g., 'mp3', 'wav')
            target_format: Target format

        Returns:
            Converted audio bytes or None
        """
        # This would require ffmpeg or pydub for actual conversion
        # For now, return as-is
        logger.warning("Audio format conversion not implemented - returning original")
        return audio_data
