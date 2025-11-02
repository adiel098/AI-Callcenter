"""
Celery tasks with OpenAI Function Calling support
Enhanced version that allows LLM to use tools during calls
"""
from celery import Task
import logging
from datetime import datetime, timedelta

from backend.workers.celery_app import celery_app
from backend.database import get_db_context
from backend.models import Lead, Call, CallOutcome, LeadStatus, Meeting, MeetingStatus, ConversationHistory, SpeakerRole
from backend.services import TwilioService, SpeechService, CalendarService
from backend.services.llm_service import LLMService, ConversationIntent
from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CallTask(Task):
    """
    Base task class with reusable service instances.
    Lazy-loads services only when needed.
    """
    _twilio = None
    _speech = None
    _llm = None
    _calendar = None

    @property
    def twilio(self):
        """Twilio service for making phone calls"""
        if self._twilio is None:
            self._twilio = TwilioService()
        return self._twilio

    @property
    def speech(self):
        """Speech service for STT (Deepgram) and TTS (ElevenLabs)"""
        if self._speech is None:
            self._speech = SpeechService()
        return self._speech

    @property
    def llm(self):
        """LLM service with function calling for conversation"""
        if self._llm is None:
            # Initialize LLM with calendar service for tool execution
            self._llm = LLMService(calendar_service=self.calendar)
        return self._llm

    @property
    def calendar(self):
        """Calendar service for booking meetings"""
        if self._calendar is None:
            self._calendar = CalendarService()
        return self._calendar


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

            # Update lead status
            lead.status = LeadStatus.CALLING

            # Create call record
            call = Call(
                lead_id=lead.id,
                language=lead.language,
                outcome=CallOutcome.IN_PROGRESS
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
                call.outcome = CallOutcome.FAILED
                call.ended_at = datetime.utcnow()
                lead.status = LeadStatus.FAILED
                db.commit()

                return {"success": False, "error": "Failed to initiate call"}

    except Exception as e:
        logger.error(f"Error initiating call: {str(e)}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(base=CallTask, bind=True)
def process_conversation_turn(
    self,
    call_id: int,
    user_message: str
):
    """
    Process conversation turn with tool calling support

    The LLM can now:
    - Check calendar availability
    - Book meetings in real-time
    - Send confirmation emails

    Args:
        call_id: Call ID
        user_message: User's transcribed speech
    """
    try:
        with get_db_context() as db:
            call = db.query(Call).filter(Call.id == call_id).first()

            if not call:
                logger.error(f"Call not found: {call_id}")
                return {"success": False}

            lead = db.query(Lead).filter(Lead.id == call.lead_id).first()

            # Save user message
            user_turn = ConversationHistory(
                call_id=call.id,
                role=SpeakerRole.USER,
                message=user_message
            )
            db.add(user_turn)
            db.commit()

            # Get conversation history
            history = db.query(ConversationHistory).filter(
                ConversationHistory.call_id == call_id
            ).order_by(ConversationHistory.created_at).all()

            conversation_messages = [
                {
                    "role": "assistant" if turn.role == SpeakerRole.AI else "user",
                    "content": turn.message
                }
                for turn in history
            ]

            # Get LLM response WITH TOOLS
            import asyncio
            loop = asyncio.get_event_loop()
            intent, ai_response, tool_calls = loop.run_until_complete(
                self.llm.get_response_with_tools(
                    user_message=user_message,
                    conversation_history=conversation_messages[:-1],
                    language=call.language or 'en',
                    lead_info={"name": lead.name, "email": lead.email}
                )
            )

            logger.info(f"[TOOLS] Intent: {intent}, Tools used: {len(tool_calls) if tool_calls else 0}")

            if tool_calls:
                for tool_call in tool_calls:
                    logger.info(f"  → {tool_call['tool']}: {tool_call['result']}")

                    # If meeting was booked, save to database
                    if tool_call['tool'] == 'book_meeting' and tool_call['result'].get('success'):
                        meeting_args = tool_call['args']
                        meeting_datetime = datetime.fromisoformat(meeting_args['datetime'])

                        meeting = Meeting(
                            lead_id=lead.id,
                            call_id=call.id,
                            scheduled_time=meeting_datetime,
                            guest_email=meeting_args['guest_email'],
                            calendar_event_id=tool_call['result'].get('meeting_id'),
                            status=MeetingStatus.SCHEDULED
                        )
                        db.add(meeting)

                        # Update call and lead
                        call.outcome = CallOutcome.MEETING_SCHEDULED
                        lead.status = LeadStatus.MEETING_SCHEDULED

                        logger.info(f"[TOOLS] ✅ Meeting booked! Event ID: {meeting.calendar_event_id}")

            # Save AI response
            ai_turn = ConversationHistory(
                call_id=call.id,
                role=SpeakerRole.AI,
                message=ai_response
            )
            db.add(ai_turn)

            # Handle intent
            if intent == ConversationIntent.MEETING_BOOKED:
                logger.info(f"[TOOLS] Meeting successfully booked via function calling!")
                call.outcome = CallOutcome.MEETING_SCHEDULED

            elif intent == ConversationIntent.NOT_INTERESTED:
                call.outcome = CallOutcome.NOT_INTERESTED
                lead.status = LeadStatus.NOT_INTERESTED

            elif intent == ConversationIntent.END_CALL:
                if call.outcome == CallOutcome.IN_PROGRESS:
                    call.outcome = CallOutcome.COMPLETED
                call.ended_at = datetime.utcnow()

            db.commit()

            return {
                "success": True,
                "intent": intent,
                "ai_response": ai_response,
                "tools_used": [tc['tool'] for tc in tool_calls] if tool_calls else [],
                "meeting_booked": intent == ConversationIntent.MEETING_BOOKED
            }

    except Exception as e:
        logger.error(f"Error processing conversation: {str(e)}")
        return {"success": False, "error": str(e)}


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

            call.transcript = "\n".join(transcript_lines)

            # Check if meeting was booked
            meeting = db.query(Meeting).filter(Meeting.call_id == call_id).first()

            # Generate summary
            conversation_messages = [
                {"role": turn.role.value, "content": turn.message}
                for turn in history
            ]

            import asyncio
            loop = asyncio.get_event_loop()
            summary = loop.run_until_complete(
                self.llm.summarize_call(conversation_messages, call.language or 'en')
            )

            if meeting:
                summary += f" | Meeting booked: {meeting.scheduled_time.isoformat()}"

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
    "process_conversation_turn",
    "finalize_call"
]
