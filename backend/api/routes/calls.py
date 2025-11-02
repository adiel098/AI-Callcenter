"""
Calls API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from backend.database import get_db
from backend.models import Call, CallOutcome, ConversationHistory, SpeakerRole

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class ConversationTurn(BaseModel):
    role: str
    message: str
    created_at: str

    class Config:
        from_attributes = True


class CallResponse(BaseModel):
    id: int
    lead_id: int
    twilio_call_sid: Optional[str]
    recording_url: Optional[str]
    transcript: Optional[str]
    duration: Optional[float]
    language: Optional[str]
    outcome: str
    started_at: str
    ended_at: Optional[str]

    class Config:
        from_attributes = True


class CallDetailResponse(CallResponse):
    conversation_history: List[ConversationTurn]


@router.get("/", response_model=List[CallResponse])
async def get_calls(
    page: int = 1,
    page_size: int = 50,
    outcome: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of calls with pagination"""
    try:
        query = db.query(Call)

        if outcome:
            query = query.filter(Call.outcome == outcome)

        # Order by most recent first
        query = query.order_by(Call.started_at.desc())

        # Paginate
        calls = query.offset((page - 1) * page_size).limit(page_size).all()

        return [
            CallResponse(
                id=call.id,
                lead_id=call.lead_id,
                twilio_call_sid=call.twilio_call_sid,
                recording_url=call.recording_url,
                transcript=call.transcript,
                duration=call.duration,
                language=call.language,
                outcome=call.outcome.value,
                started_at=call.started_at.isoformat(),
                ended_at=call.ended_at.isoformat() if call.ended_at else None
            )
            for call in calls
        ]

    except Exception as e:
        logger.error(f"Failed to get calls: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}", response_model=CallDetailResponse)
async def get_call(call_id: int, db: Session = Depends(get_db)):
    """Get call details including conversation history"""
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    # Get conversation history
    conversation = db.query(ConversationHistory).filter(
        ConversationHistory.call_id == call_id
    ).order_by(ConversationHistory.created_at).all()

    return CallDetailResponse(
        id=call.id,
        lead_id=call.lead_id,
        twilio_call_sid=call.twilio_call_sid,
        recording_url=call.recording_url,
        transcript=call.transcript,
        duration=call.duration,
        language=call.language,
        outcome=call.outcome.value,
        started_at=call.started_at.isoformat(),
        ended_at=call.ended_at.isoformat() if call.ended_at else None,
        conversation_history=[
            ConversationTurn(
                role=turn.role.value,
                message=turn.message,
                created_at=turn.created_at.isoformat()
            )
            for turn in conversation
        ]
    )


@router.get("/{call_id}/recording")
async def get_call_recording(call_id: int, db: Session = Depends(get_db)):
    """Get call recording URL"""
    call = db.query(Call).filter(Call.id == call_id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    if not call.recording_url:
        raise HTTPException(status_code=404, detail="Recording not available")

    return {"recording_url": call.recording_url}
