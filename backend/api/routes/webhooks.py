"""
Webhooks API routes - for Twilio callbacks
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from backend.database import get_db
from backend.models import Call, CallOutcome, Lead, LeadStatus
from backend.services import TwilioService

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
            if call.outcome == CallOutcome.IN_PROGRESS:
                call.outcome = CallOutcome.COMPLETED

            # Update lead status
            lead = db.query(Lead).filter(Lead.id == call.lead_id).first()
            if lead:
                lead.status = LeadStatus.CONTACTED

        elif call_status in ['busy', 'no-answer', 'failed']:
            call.ended_at = datetime.utcnow()
            call.outcome = CallOutcome.NO_ANSWER if call_status == 'no-answer' else CallOutcome.FAILED

            # Update lead
            lead = db.query(Lead).filter(Lead.lead_id == call.lead_id).first()
            if lead:
                lead.status = LeadStatus.NO_ANSWER

        db.commit()

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Twilio status callback error: {str(e)}")
        return {"status": "error", "message": str(e)}


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
    This is called after user speaks
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

        # This is where you would:
        # 1. Save the user's speech to conversation history
        # 2. Call LLM service to get response
        # 3. Generate TTS
        # 4. Return TwiML with AI response

        # For now, return a simple response
        language = call.language or 'en'
        twiml = twilio_service.generate_twiml_response(
            "Thank you for your response. We'll be in touch soon. Goodbye!",
            language,
            end_call=True
        )

        from fastapi.responses import Response
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        logger.error(f"Process speech error: {str(e)}")
        error_twiml = '<Response><Say>Error processing your response. Goodbye.</Say></Response>'
        from fastapi.responses import Response
        return Response(content=error_twiml, media_type="application/xml")
