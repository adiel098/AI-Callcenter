"""
Speech services for STT (Deepgram) and TTS (ElevenLabs)
"""
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from elevenlabs.client import ElevenLabs
from elevenlabs import Voice, VoiceSettings
import httpx
import logging
from typing import Optional, AsyncIterator
import io

from config import get_settings
from utils.language_detector import get_deepgram_language_code, get_voice_for_language

logger = logging.getLogger(__name__)
settings = get_settings()


class SpeechService:
    """Service for speech-to-text and text-to-speech operations"""

    def __init__(self):
        # Initialize Deepgram client (v3 SDK)
        self.deepgram_client = DeepgramClient(settings.deepgram_api_key)

        # Initialize ElevenLabs client
        self.elevenlabs_client = ElevenLabs(api_key=settings.elevenlabs_api_key)

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

            # Configure Deepgram options (v3 SDK)
            options = PrerecordedOptions(
                model="nova-2",
                language=deepgram_language,
                smart_format=True,
                punctuate=True,
                diarize=False
            )

            # Create payload (v3 SDK)
            payload = FileSource(buffer=audio_data)

            # Transcribe
            response = self.deepgram_client.listen.rest.v("1").transcribe_file(
                payload,
                options
            )

            # Extract transcript
            if response.results and response.results.channels:
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
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75,
                        style=0.0,
                        use_speaker_boost=True
                    )
                ),
                model="eleven_multilingual_v2"  # Supports multiple languages
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
            audio_generator = self.elevenlabs_client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75
                    )
                ),
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
            voices = self.elevenlabs_client.voices.get_all()
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "labels": voice.labels
                }
                for voice in voices.voices
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
