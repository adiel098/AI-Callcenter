"""
Webhooks API routes - for Twilio callbacks
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from backend.database import get_db
from backend.models import Call, CallOutcome, Lead, LeadStatus, Meeting, MeetingStatus
from backend.services import TwilioService
from backend.workers.tasks import finalize_call

logger = logging.getLogger(__name__)
router = APIRouter()
twilio_service = TwilioService()


@router.post("/twilio/status")
async def twilio_status_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Twilio call status updates
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get('CallSid')
        call_status = form_data.get('CallStatus')
        call_duration = form_data.get('CallDuration')

        logger.info(f"Twilio status callback: {call_sid} - {call_status}")

        # Find call in database
        call = db.query(Call).filter(Call.twilio_call_sid == call_sid).first()

        if not call:
            logger.warning(f"Call not found: {call_sid}")
            return {"status": "ok"}

        # Update call based on status
        if call_status == 'completed':
            call.ended_at = datetime.utcnow()
            if call_duration:
                call.duration = float(call_duration)

            # Get recording URL if available
            recording_url = twilio_service.get_call_recording_url(call_sid)
            if recording_url:
                call.recording_url = recording_url

            # Update call outcome if not already set
            # Don't override if outcome was already set during call (INTERESTED, NOT_INTERESTED, BUSY)
            if call.outcome not in [CallOutcome.INTERESTED, CallOutcome.NOT_INTERESTED, CallOutcome.BUSY]:
                call.outcome = CallOutcome.BUSY  # Default for completed calls

            # Update lead status
            lead = db.query(Lead).filter(Lead.id == call.lead_id).first()
            if lead:
                lead.status = LeadStatus.CONTACTED

            # Trigger finalization task to generate transcript and summary
            finalize_call.delay(call.id)
            logger.info(f"Triggered finalize_call task for call {call.id}")

        elif call_status in ['busy', 'no-answer', 'failed']:
            call.ended_at = datetime.utcnow()
            call.outcome = CallOutcome.NO_ANSWER  # Map all technical failures to NO_ANSWER

            # Update lead
            lead = db.query(Lead).filter(Lead.id == call.lead_id).first()
            if lead:
                lead.status = LeadStatus.NO_ANSWER

        db.commit()

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Twilio status callback error: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twilio/voice")
async def twilio_voice_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Twilio voice callback (when call is answered)
    This returns TwiML instructions
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get('CallSid')
        from_number = form_data.get('From')

        logger.info(f"Twilio voice callback: {call_sid}")

        # Find the call
        call = db.query(Call).filter(Call.twilio_call_sid == call_sid).first()

        if not call:
            # Return generic TwiML
            return twilio_service.generate_twiml_greeting()

        # Get language from call
        language = call.language or 'en'

        # Generate TwiML greeting
        twiml = twilio_service.generate_twiml_greeting(language)

        from fastapi.responses import Response
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Twilio voice callback error: {str(e)}")
        # Return error TwiML
        error_twiml = '<Response><Say>We are experiencing technical difficulties. Goodbye.</Say></Response>'
        from fastapi.responses import Response
        return Response(content=error_twiml, media_type="application/xml")


@router.post("/twilio/process-speech")
async def twilio_process_speech(request: Request, db: Session = Depends(get_db)):
    """
    Process speech input from Twilio
    This is called after user speaks and processes the conversation with AI
    """
    try:
        form_data = await request.form()
        call_sid = form_data.get('CallSid')
        speech_result = form_data.get('SpeechResult')

        logger.info(f"Speech received from {call_sid}: {speech_result}")

        # Find call
        call = db.query(Call).filter(Call.twilio_call_sid == call_sid).first()

        if not call:
            error_twiml = '<Response><Say>Error processing your response. Goodbye.</Say></Response>'
            from fastapi.responses import Response
            return Response(content=error_twiml, media_type="application/xml")

        if not speech_result or speech_result.strip() == '':
            # No speech detected, ask user to repeat
            language = call.language or 'en'
            twiml = twilio_service.generate_twiml_response(
                "I didn't catch that. Could you please repeat?",
                language,
                end_call=False
            )
            from fastapi.responses import Response
            return Response(content=twiml, media_type="application/xml")

        # Import Celery task
        from backend.workers.tasks import process_conversation_turn
        from backend.models import ConversationHistory, SpeakerRole, Lead
        from backend.services import LLMService, CalendarService
        from backend.services.llm_service import ConversationIntent

        # Get language
        language = call.language or 'en'

        # Process conversation synchronously (since webhook needs immediate response)
        # We cannot use Celery here because Twilio needs TwiML response immediately
        lead = db.query(Lead).filter(Lead.id == call.lead_id).first()

        # Save user message
        user_turn = ConversationHistory(
            call_id=call.id,
            role=SpeakerRole.USER,
            message=speech_result
        )
        db.add(user_turn)
        db.commit()

        # Get conversation history
        history = db.query(ConversationHistory).filter(
            ConversationHistory.call_id == call.id
        ).order_by(ConversationHistory.created_at).all()

        conversation_messages = [
            {
                "role": "assistant" if turn.role == SpeakerRole.AI else "user",
                "content": turn.message
            }
            for turn in history
        ]

        # Initialize services
        calendar_service = CalendarService()
        llm_service = LLMService(calendar_service=calendar_service)

        # Get LLM response with tools
        intent, ai_response, tool_calls = await llm_service.get_response_with_tools(
            user_message=speech_result,
            conversation_history=conversation_messages[:-1],
            lead_info={"name": lead.name if lead else "there", "email": lead.email if lead else ""}
        )

        logger.info(f"AI Intent: {intent}, Tools used: {len(tool_calls) if tool_calls else 0}")

        # Handle tool calls (e.g., meeting booking)
        if tool_calls:
            for tool_call in tool_calls:
                logger.info(f"Tool executed: {tool_call['tool']}")

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
                    call.outcome = CallOutcome.INTERESTED  # Meeting scheduled = interested
                    if lead:
                        lead.status = LeadStatus.MEETING_SCHEDULED

                    logger.info(f"✅ Meeting booked! Event ID: {meeting.calendar_event_id}")

        # Save AI response
        ai_turn = ConversationHistory(
            call_id=call.id,
            role=SpeakerRole.AI,
            message=ai_response
        )
        db.add(ai_turn)

        # Determine if we should end the call and set outcome
        end_call = False

        if intent == ConversationIntent.MEETING_BOOKED:
            logger.info("Meeting successfully booked, will end call after confirmation")
            call.outcome = CallOutcome.INTERESTED  # Meeting scheduled = interested
            end_call = True

        elif intent == ConversationIntent.NOT_INTERESTED:
            logger.info("User not interested, ending call")
            call.outcome = CallOutcome.NOT_INTERESTED
            if lead:
                lead.status = LeadStatus.NOT_INTERESTED
            end_call = True

        elif intent == ConversationIntent.END_CALL:
            logger.info("Conversation complete, ending call")
            # If no outcome set yet, mark as BUSY (interested but no meeting)
            if call.outcome not in [CallOutcome.INTERESTED, CallOutcome.NOT_INTERESTED]:
                call.outcome = CallOutcome.BUSY
            call.ended_at = datetime.utcnow()
            end_call = True

        elif intent in [ConversationIntent.INTERESTED, ConversationIntent.SCHEDULE_MEETING]:
            # User shows interest or is scheduling - mark as BUSY for now
            logger.info(f"User interested, continuing conversation with intent: {intent}")
            call.outcome = CallOutcome.BUSY  # Interested but no meeting yet
            end_call = False

        else:
            # NEEDS_INFO - continue conversation
            logger.info(f"Continuing conversation with intent: {intent}")
            end_call = False

        db.commit()

        # Generate TwiML with AI response
        # Using Twilio's built-in TTS (faster response time than ElevenLabs)
        twiml = twilio_service.generate_twiml_response(
            ai_response,
            language,
            end_call=end_call
        )

        from fastapi.responses import Response
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Process speech error: {str(e)}", exc_info=True)
        db.rollback()
        error_twiml = '<Response><Say>I apologize, but I encountered a technical issue. Please try calling back. Goodbye.</Say><Hangup/></Response>'
        from fastapi.responses import Response
        return Response(content=error_twiml, media_type="application/xml")
