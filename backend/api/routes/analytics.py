"""
Analytics API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
import logging
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import Lead, Call, Meeting, CallOutcome, LeadStatus, MeetingStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class AnalyticsOverview(BaseModel):
    total_leads: int
    total_calls: int
    total_meetings: int
    meetings_scheduled_today: int
    calls_today: int
    conversion_rate: float
    average_call_duration: float


class CallOutcomeStats(BaseModel):
    outcome: str
    count: int


class LanguageStats(BaseModel):
    language: str
    count: int


class VoicePerformanceStats(BaseModel):
    voice_id: str
    voice_name: str
    total_calls: int
    meetings_booked: int
    conversion_rate: float
    avg_duration: float


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall analytics overview"""
    try:
        # Total counts
        total_leads = db.query(func.count(Lead.id)).scalar()
        total_calls = db.query(func.count(Call.id)).scalar()
        total_meetings = db.query(func.count(Meeting.id)).filter(
            Meeting.status == MeetingStatus.SCHEDULED
        ).scalar()

        # Today's counts
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        calls_today = db.query(func.count(Call.id)).filter(
            Call.started_at >= today_start
        ).scalar()

        meetings_today = db.query(func.count(Meeting.id)).filter(
            Meeting.created_at >= today_start,
            Meeting.status == MeetingStatus.SCHEDULED
        ).scalar()

        # Conversion rate (meetings / calls)
        conversion_rate = (total_meetings / total_calls * 100) if total_calls > 0 else 0.0

        # Average call duration
        avg_duration = db.query(func.avg(Call.duration)).filter(
            Call.duration.isnot(None)
        ).scalar() or 0.0

        return AnalyticsOverview(
            total_leads=total_leads or 0,
            total_calls=total_calls or 0,
            total_meetings=total_meetings or 0,
            meetings_scheduled_today=meetings_today or 0,
            calls_today=calls_today or 0,
            conversion_rate=round(conversion_rate, 2),
            average_call_duration=round(float(avg_duration), 2)
        )

    except Exception as e:
        logger.error(f"Failed to get analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/call-outcomes")
async def get_call_outcomes(db: Session = Depends(get_db)):
    """Get call outcome distribution"""
    try:
        outcomes = db.query(
            Call.outcome,
            func.count(Call.id).label('count')
        ).group_by(Call.outcome).all()

        return {
            "outcomes": [
                {"outcome": outcome.value, "count": count}
                for outcome, count in outcomes
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get call outcomes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/language-distribution")
async def get_language_distribution(db: Session = Depends(get_db)):
    """Get language distribution of calls"""
    try:
        languages = db.query(
            Call.language,
            func.count(Call.id).label('count')
        ).filter(
            Call.language.isnot(None)
        ).group_by(Call.language).all()

        return {
            "languages": [
                {"language": language, "count": count}
                for language, count in languages
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get language distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls-over-time")
async def get_calls_over_time(days: int = 7, db: Session = Depends(get_db)):
    """Get calls over time (last N days)"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)

        # Query calls grouped by date
        from sqlalchemy import cast, Date

        calls_by_date = db.query(
            cast(Call.started_at, Date).label('date'),
            func.count(Call.id).label('count')
        ).filter(
            Call.started_at >= start_date
        ).group_by(cast(Call.started_at, Date)).order_by('date').all()

        return {
            "data": [
                {"date": str(date), "count": count}
                for date, count in calls_by_date
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get calls over time: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lead-status-distribution")
async def get_lead_status_distribution(db: Session = Depends(get_db)):
    """
    Get lead status distribution
    Returns count of leads in each status
    """
    try:
        statuses = db.query(
            Lead.status,
            func.count(Lead.id).label('count')
        ).group_by(Lead.status).all()

        # Calculate total for percentage
        total_leads = sum(count for _, count in statuses)

        return {
            "statuses": [
                {
                    "status": status.value,
                    "count": count,
                    "percentage": round((count / total_leads * 100), 2) if total_leads > 0 else 0
                }
                for status, count in statuses
            ],
            "total": total_leads
        }

    except Exception as e:
        logger.error(f"Failed to get lead status distribution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-activity")
async def get_recent_activity(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent activity from calls, meetings, and leads"""
    try:
        activities = []

        # Get recent calls
        recent_calls = db.query(Call).join(Lead, Call.lead_id == Lead.id).order_by(
            Call.started_at.desc()
        ).limit(limit).all()

        for call in recent_calls:
            if call.started_at:
                # Determine status based on outcome
                status = "success" if call.outcome == CallOutcome.INTERESTED else "error" if call.outcome in [CallOutcome.NO_ANSWER, CallOutcome.NOT_INTERESTED] else "info"

                # Create description based on outcome
                description = call.summary[:100] if call.summary else (call.outcome.value.replace('_', ' ').title() if call.outcome else "Unknown outcome")

                activities.append({
                    "id": f"call-{call.id}",
                    "type": "call",
                    "title": f"Call with {call.lead.name if call.lead else 'Unknown'}",
                    "description": description,
                    "time": call.started_at.isoformat(),
                    "status": status
                })

        # Get recent meetings
        recent_meetings = db.query(Meeting).join(Lead, Meeting.lead_id == Lead.id).order_by(
            Meeting.created_at.desc()
        ).limit(limit).all()

        for meeting in recent_meetings:
            activities.append({
                "id": f"meeting-{meeting.id}",
                "type": "meeting",
                "title": f"Meeting scheduled with {meeting.lead.name if meeting.lead else 'Unknown'}",
                "description": f"{meeting.scheduled_time.strftime('%A at %I:%M %p')}",
                "time": meeting.created_at.isoformat(),
                "status": "success"
            })

        # Get recent lead imports (count leads created in batches within 5 minutes)
        # This is a simple approach - group leads by creation time rounded to 5 min intervals
        from sqlalchemy import desc
        recent_leads = db.query(Lead).order_by(desc(Lead.created_at)).limit(limit * 5).all()

        lead_batches = {}
        for lead in recent_leads:
            # Round to 5-minute intervals
            rounded_time = lead.created_at.replace(second=0, microsecond=0)
            interval = rounded_time.minute // 5
            rounded_time = rounded_time.replace(minute=interval * 5)

            if rounded_time not in lead_batches:
                lead_batches[rounded_time] = 0
            lead_batches[rounded_time] += 1

        # Add lead batch imports as activities
        for batch_time, count in list(lead_batches.items())[:5]:
            if count > 5:  # Only show if more than 5 leads (likely a CSV upload)
                activities.append({
                    "id": f"leads-{batch_time.isoformat()}",
                    "type": "lead",
                    "title": f"{count} new leads uploaded",
                    "description": "CSV import completed",
                    "time": batch_time.isoformat(),
                    "status": "info"
                })

        # Sort all activities by time (most recent first)
        activities.sort(key=lambda x: x["time"], reverse=True)

        # Return top N activities
        return {"activities": activities[:limit]}

    except Exception as e:
        logger.error(f"Failed to get recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-campaigns")
async def get_active_campaigns(db: Session = Depends(get_db)):
    """Get active campaigns status"""
    try:
        # Count leads by status to show campaign progress
        status_counts = db.query(
            Lead.status,
            func.count(Lead.id).label('count')
        ).group_by(Lead.status).all()

        status_dict = {status.value: count for status, count in status_counts}

        # Get total leads
        total_leads = sum(status_dict.values())

        # Calculate active campaign metrics
        queued = status_dict.get('queued', 0)
        calling = status_dict.get('calling', 0)
        contacted = status_dict.get('contacted', 0)

        # Consider a campaign "active" if there are queued or calling leads
        is_active = queued > 0 or calling > 0

        # Calculate progress (contacted out of total)
        completed = contacted + status_dict.get('meeting_scheduled', 0)
        progress = (completed / total_leads * 100) if total_leads > 0 else 0

        return {
            "campaigns": [
                {
                    "name": "Outbound Campaign",
                    "is_active": is_active,
                    "queued": queued,
                    "calling": calling,
                    "completed": completed,
                    "total": total_leads,
                    "progress": round(progress, 1)
                }
            ]
        }

    except Exception as e:
        logger.error(f"Failed to get active campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice-performance", response_model=list[VoicePerformanceStats])
async def get_voice_performance(db: Session = Depends(get_db)):
    """
    Get voice performance statistics.

    Returns performance metrics for each voice used in calls:
    - Total calls made with each voice
    - Meetings successfully booked
    - Conversion rate (meetings/calls)
    - Average call duration
    """
    try:
        # Query calls grouped by voice_id
        # Only include calls that have a voice_id set
        voice_stats = db.query(
            Call.voice_id,
            Call.voice_name,
            func.count(Call.id).label('total_calls'),
            func.count(Meeting.id).label('meetings_booked'),
            func.avg(Call.duration).label('avg_duration')
        ).outerjoin(
            Meeting, Call.id == Meeting.call_id
        ).filter(
            Call.voice_id.isnot(None)
        ).group_by(
            Call.voice_id,
            Call.voice_name
        ).all()

        results = []
        for stat in voice_stats:
            conversion_rate = (stat.meetings_booked / stat.total_calls * 100) if stat.total_calls > 0 else 0.0
            avg_duration = float(stat.avg_duration) if stat.avg_duration else 0.0

            results.append(VoicePerformanceStats(
                voice_id=stat.voice_id,
                voice_name=stat.voice_name or "Unknown",
                total_calls=stat.total_calls,
                meetings_booked=stat.meetings_booked,
                conversion_rate=round(conversion_rate, 2),
                avg_duration=round(avg_duration, 2)
            ))

        # Sort by total calls (most used voices first)
        results.sort(key=lambda x: x.total_calls, reverse=True)

        logger.info(f"Voice performance stats retrieved: {len(results)} voices")
        return results

    except Exception as e:
        logger.error(f"Failed to get voice performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
