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
