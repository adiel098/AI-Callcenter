"""
Meetings API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from backend.database import get_db
from backend.models import Meeting, MeetingStatus, Lead

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class MeetingResponse(BaseModel):
    id: int
    lead_id: int
    lead_name: str
    call_id: Optional[int]
    scheduled_at: str  # Changed from scheduled_time
    email: Optional[str]  # Changed from guest_email
    duration: Optional[int]
    meeting_link: Optional[str]
    notes: Optional[str]
    calendar_event_id: Optional[str]
    status: str
    created_at: str

    class Config:
        from_attributes = True


class MeetingsListResponse(BaseModel):
    meetings: List[MeetingResponse]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=MeetingsListResponse)
async def get_meetings(
    page: int = 1,
    page_size: int = 50,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of meetings"""
    try:
        # JOIN with Lead table to get lead name
        query = db.query(Meeting, Lead).join(Lead, Meeting.lead_id == Lead.id)

        if status:
            query = query.filter(Meeting.status == status)

        # Get total count
        total = query.count()

        # Order by scheduled time
        query = query.order_by(Meeting.scheduled_time.desc())

        # Paginate
        results = query.offset((page - 1) * page_size).limit(page_size).all()

        meetings = [
            MeetingResponse(
                id=meeting.id,
                lead_id=meeting.lead_id,
                lead_name=lead.name,
                call_id=meeting.call_id,
                scheduled_at=meeting.scheduled_time.isoformat(),
                email=meeting.guest_email,
                duration=meeting.duration,
                meeting_link=meeting.meeting_link,
                notes=meeting.notes,
                calendar_event_id=meeting.calendar_event_id,
                status=meeting.status.value,
                created_at=meeting.created_at.isoformat()
            )
            for meeting, lead in results
        ]

        return MeetingsListResponse(
            meetings=meetings,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Failed to get meetings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    """Get meeting details"""
    # JOIN with Lead table to get lead name
    result = db.query(Meeting, Lead).join(Lead, Meeting.lead_id == Lead.id).filter(Meeting.id == meeting_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting, lead = result

    return MeetingResponse(
        id=meeting.id,
        lead_id=meeting.lead_id,
        lead_name=lead.name,
        call_id=meeting.call_id,
        scheduled_at=meeting.scheduled_time.isoformat(),
        email=meeting.guest_email,
        duration=meeting.duration,
        meeting_link=meeting.meeting_link,
        notes=meeting.notes,
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
