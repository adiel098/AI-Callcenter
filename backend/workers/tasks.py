"""
Celery tasks with OpenAI Function Calling support
Enhanced version that allows LLM to use tools during calls
"""
from celery import Task
import logging
from datetime import datetime, timedelta

from backend.workers.celery_app import celery_app
from backend.database import get_db_context
from backend.models import Lead, Call, CallOutcome, LeadStatus, Meeting, MeetingStatus, ConversationHistory, SpeakerRole, Setting
from backend.services import TwilioService, CalendarService
from backend.services.llm_service import LLMService, ConversationIntent
from backend.services.zoom_service import ZoomService
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CallTask(Task):
    """
    Base task class with reusable service instances.
    Lazy-loads services only when needed.
    """
    _twilio = None
    _llm = None
    _calendar = None
    _zoom = None

    @property
    def twilio(self):
        """Twilio service for making phone calls"""
        if self._twilio is None:
            self._twilio = TwilioService()
        return self._twilio

    @property
    def llm(self):
        """LLM service with function calling for conversation"""
        if self._llm is None:
            # Initialize LLM with calendar and zoom services for tool execution
            self._llm = LLMService(
                calendar_service=self.calendar,
                zoom_service=self.zoom
            )
        return self._llm

    @property
    def calendar(self):
        """Calendar service for booking meetings"""
        if self._calendar is None:
            self._calendar = CalendarService()
        return self._calendar

    @property
    def zoom(self):
        """Zoom service for video conference links"""
        if self._zoom is None:
            self._zoom = ZoomService()
        return self._zoom


@celery_app.task(base=CallTask, bind=True, max_retries=3)
def initiate_call(self, lead_id: int):
    """
    Initiate an outbound call with tool support

    Args:
        lead_id: Lead ID to call
    """
    try:
        with get_db_context() as db:
            lead = db.query(Lead).filter(Lead.id == lead_id).first()

            if not lead:
                logger.error(f"Lead not found: {lead_id}")
                return {"success": False, "error": "Lead not found"}

            logger.info(f"[TOOLS] Initiating call to {lead.name} ({lead.phone}) with function calling enabled")

            # Check if lead already has an active call (prevents duplicates)
            active_call = db.query(Call).filter(
                Call.lead_id == lead_id,
                Call.ended_at.is_(None)
            ).first()

            if active_call:
                logger.warning(f"Lead {lead_id} already has active call {active_call.id} (SID: {active_call.twilio_call_sid}), skipping duplicate")
                return {
                    "success": False,
                    "error": "Call already in progress",
                    "active_call_id": active_call.id
                }

            # Update lead status
            lead.status = LeadStatus.CALLING

            # Fetch default voice settings (if set)
            voice_id_setting = db.query(Setting).filter(Setting.key == "default_voice_id").first()
            voice_name_setting = db.query(Setting).filter(Setting.key == "default_voice_name").first()

            voice_id = voice_id_setting.value if voice_id_setting else None
            voice_name = voice_name_setting.value if voice_name_setting else None

            if voice_id:
                logger.info(f"[VOICE] Using default voice: {voice_name} ({voice_id})")
            else:
                logger.info(f"[VOICE] No default voice set, will use language-based selection")

            # Create call record (no outcome set yet - will be set during/after call)
            call = Call(
                lead_id=lead.id,
                language=lead.language,
                voice_id=voice_id,
                voice_name=voice_name,
                outcome=None
            )
            db.add(call)
            db.commit()
            db.refresh(call)

            # Construct callback URLs
            callback_url = f"{settings.api_base_url}/api/webhooks/twilio/voice"
            status_callback_url = f"{settings.api_base_url}/api/webhooks/twilio/status"

            # Initiate Twilio call
            call_sid = self.twilio.initiate_call(
                to_phone_number=lead.phone,
                callback_url=callback_url,
                status_callback_url=status_callback_url
            )

            if call_sid:
                call.twilio_call_sid = call_sid
                db.commit()

                logger.info(f"[TOOLS] Call initiated: {call_sid} (LLM can now use calendar tools)")

                return {
                    "success": True,
                    "call_id": call.id,
                    "call_sid": call_sid,
                    "tools_enabled": True
                }
            else:
                call.outcome = CallOutcome.NO_ANSWER  # Failed to initiate = no answer
                call.ended_at = datetime.utcnow()
                lead.status = LeadStatus.NO_ANSWER
                db.commit()

                return {"success": False, "error": "Failed to initiate call"}

    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        raise self.retry(exc=e, countdown=60)




@celery_app.task(base=CallTask, bind=True)
def finalize_call(self, call_id: int):
    """
    Finalize call with tool usage summary

    Args:
        call_id: Call ID
    """
    try:
        with get_db_context() as db:
            call = db.query(Call).filter(Call.id == call_id).first()

            if not call:
                return {"success": False}

            # Get conversation history
            history = db.query(ConversationHistory).filter(
                ConversationHistory.call_id == call_id
            ).order_by(ConversationHistory.created_at).all()

            # Generate transcript
            transcript_lines = []
            for turn in history:
                speaker = "AI" if turn.role == SpeakerRole.AI else "User"
                transcript_lines.append(f"{speaker}: {turn.message}")

            transcript_text = "\n".join(transcript_lines)
            call.transcript = transcript_text

            # Check if meeting was booked
            meeting = db.query(Meeting).filter(Meeting.call_id == call_id).first()

            # Generate summary using the transcript text
            import asyncio
            loop = asyncio.get_event_loop()
            summary = loop.run_until_complete(
                self.llm.summarize_call(transcript_text)
            )

            if meeting:
                summary += f" | Meeting booked: {meeting.scheduled_time.isoformat()}"

            # Store the summary in the database
            call.summary = summary
            logger.info(f"[TOOLS] Call {call_id} summary: {summary}")

            db.commit()

            return {
                "success": True,
                "summary": summary,
                "meeting_booked": meeting is not None,
                "meeting_id": meeting.id if meeting else None
            }

    except Exception as e:
        logger.error(f"Error finalizing call: {str(e)}")
        return {"success": False, "error": str(e)}


__all__ = [
    "initiate_call",
    "finalize_call"
]
