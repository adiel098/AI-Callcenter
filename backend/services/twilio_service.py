"""
Twilio integration service for outbound calling
"""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Say
from typing import Optional, Dict
import logging

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class TwilioService:
    """Service for managing Twilio phone calls"""

    def __init__(self):
        self.client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token
        )
        self.phone_number = settings.twilio_phone_number

    def initiate_call(
        self,
        to_phone_number: str,
        callback_url: str,
        status_callback_url: str
    ) -> Optional[str]:
        """
        Initiate an outbound call

        Args:
            to_phone_number: Phone number to call (E.164 format)
            callback_url: URL for voice/TwiML instructions
            status_callback_url: URL for call status updates

        Returns:
            Call SID if successful, None otherwise
        """
        try:
            call = self.client.calls.create(
                to=to_phone_number,
                from_=self.phone_number,
                url=callback_url,
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                status_callback_method='POST',
                record=True,  # Enable call recording
                timeout=30,  # Ring timeout in seconds
                machine_detection='DetectMessageEnd'  # Detect voicemail
            )

            logger.info(f"Call initiated to {to_phone_number}: SID={call.sid}")
            return call.sid

        except Exception as e:
            logger.error(f"Failed to initiate call to {to_phone_number}: {str(e)}")
            return None

    def get_call_status(self, call_sid: str) -> Optional[Dict]:
        """
        Get current status of a call

        Args:
            call_sid: Twilio Call SID

        Returns:
            Dictionary with call details or None
        """
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "from": call.from_,
                "to": call.to,
                "direction": call.direction,
                "answered_by": call.answered_by
            }
        except Exception as e:
            logger.error(f"Failed to fetch call {call_sid}: {str(e)}")
            return None

    def get_call_recording_url(self, call_sid: str) -> Optional[str]:
        """
        Get recording URL for a completed call

        Args:
            call_sid: Twilio Call SID

        Returns:
            Recording URL or None
        """
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)
            if recordings:
                # Get the first recording
                recording = recordings[0]
                # Construct full URL
                base_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}"
                return f"{base_url}/Recordings/{recording.sid}.mp3"
            return None
        except Exception as e:
            logger.error(f"Failed to fetch recording for call {call_sid}: {str(e)}")
            return None

    def terminate_call(self, call_sid: str) -> bool:
        """
        Terminate an active call

        Args:
            call_sid: Twilio Call SID

        Returns:
            True if successful, False otherwise
        """
        try:
            call = self.client.calls(call_sid).update(status='completed')
            logger.info(f"Call {call_sid} terminated")
            return True
        except Exception as e:
            logger.error(f"Failed to terminate call {call_sid}: {str(e)}")
            return False

    @staticmethod
    def generate_twiml_greeting(language: str = "en") -> str:
        """
        Generate TwiML for initial greeting

        Args:
            language: Language code for greeting

        Returns:
            TwiML XML string
        """
        # Get settings for API base URL
        settings = get_settings()

        response = VoiceResponse()

        # Language-specific greetings
        greetings = {
            "he": "שלום! אני עוזרת הווירטואלית. אשמח לדבר איתך על תיאום פגישה.",
            "en": "Hello! I'm your virtual assistant. I'd like to speak with you about scheduling a meeting.",
            "fr": "Bonjour! Je suis votre assistant virtuel. Je voudrais vous parler de la planification d'une réunion.",
            "es": "¡Hola! Soy tu asistente virtual. Me gustaría hablar contigo sobre programar una reunión.",
            "de": "Hallo! Ich bin Ihr virtueller Assistent. Ich würde gerne mit Ihnen über die Planung eines Treffens sprechen."
        }

        # Use English for trial account compatibility (Hebrew TTS may not work)
        greeting_text = greetings.get("en")
        tts_language = "en-US"

        # Use Gather to collect speech with absolute URL
        gather = Gather(
            input='speech',
            action=f'{settings.api_base_url}/api/webhooks/twilio/process-speech',  # Absolute URL for ngrok
            method='POST',
            language=tts_language,
            speech_timeout='auto',
            timeout=5  # Increased timeout for better user experience
        )
        gather.say(greeting_text, language=tts_language)

        response.append(gather)

        # If no response, repeat
        response.say("I didn't hear anything. Goodbye!")

        return str(response)

    @staticmethod
    def generate_twiml_response(text: str, language: str = "en", end_call: bool = False) -> str:
        """
        Generate TwiML for AI response

        Args:
            text: Text to speak
            language: Language code
            end_call: Whether to end the call after this response

        Returns:
            TwiML XML string
        """
        # Get settings for API base URL
        settings = get_settings()

        response = VoiceResponse()

        # Use English for trial account compatibility
        tts_language = "en-US"

        if not end_call:
            # Continue conversation with absolute URL
            gather = Gather(
                input='speech',
                action=f'{settings.api_base_url}/api/webhooks/twilio/process-speech',  # Absolute URL for ngrok
                method='POST',
                language=tts_language,
                speech_timeout='auto',
                timeout=5  # Increased timeout for better user experience
            )
            gather.say(text, language=tts_language)
            response.append(gather)

            # Fallback if no speech detected (keeps call alive and prompts user)
            response.say("I didn't hear anything. Could you please speak?", language=tts_language)
        else:
            # End call
            response.say(text, language=tts_language)
            response.hangup()

        return str(response)

    @staticmethod
    def generate_twiml_stream(websocket_url: str) -> str:
        """
        Generate TwiML for WebSocket streaming (real-time audio)

        Args:
            websocket_url: WebSocket URL for audio streaming

        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        response.start().stream(url=websocket_url)
        response.pause(length=60)  # Keep connection open
        return str(response)
