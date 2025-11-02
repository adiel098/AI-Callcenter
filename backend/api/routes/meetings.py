"""
Meetings API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from database import get_db
from models import Meeting, MeetingStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class MeetingResponse(BaseModel):
    id: int
    lead_id: int
    call_id: Optional[int]
    scheduled_time: str
    guest_email: Optional[str]
    calendar_event_id: Optional[str]
    status: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MeetingResponse])
async def get_meetings(
    page: int = 1,
    page_size: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of meetings"""
    try:
        query = db.query(Meeting)

        if status:
            query = query.filter(Meeting.status == status)

        # Order by scheduled time
        query = query.order_by(Meeting.scheduled_time.desc())

        # Paginate
        meetings = query.offset((page - 1) * page_size).limit(page_size).all()

        return [
            MeetingResponse(
                id=meeting.id,
                lead_id=meeting.lead_id,
                call_id=meeting.call_id,
                scheduled_time=meeting.scheduled_time.isoformat(),
                guest_email=meeting.guest_email,
                calendar_event_id=meeting.calendar_event_id,
                status=meeting.status.value,
                created_at=meeting.created_at.isoformat()
            )
            for meeting in meetings
        ]

    except Exception as e:
        logger.error(f"Failed to get meetings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get meeting details"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return MeetingResponse(
        id=meeting.id,
        lead_id=meeting.lead_id,
        call_id=meeting.call_id,
        scheduled_time=meeting.scheduled_time.isoformat(),
        guest_email=meeting.guest_email,
        calendar_event_id=meeting.calendar_event_id,
        status=meeting.status.value,
        created_at=meeting.created_at.isoformat()
    )


@router.patch("/{meeting_id}/status")
async def update_meeting_status(
    meeting_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update meeting status"""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    try:
        meeting.status = MeetingStatus(status)
        db.commit()
        db.refresh(meeting)

        return {"success": True, "message": "Meeting status updated"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    except Exception as e:
        logger.error(f"Failed to update meeting: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
