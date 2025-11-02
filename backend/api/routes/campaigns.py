"""
Campaigns API routes - for initiating bulk calls
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import logging

from backend.database import get_db
from backend.models import Lead, LeadStatus

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class CampaignCreate(BaseModel):
    name: str
    lead_ids: List[int]


class CampaignResponse(BaseModel):
    success: bool
    message: str
    queued_leads: int


@router.post("/start", response_model=CampaignResponse)
async def start_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Start a call campaign for selected leads
    """
    try:
        # Validate leads exist and are eligible
        leads = db.query(Lead).filter(Lead.id.in_(campaign.lead_ids)).all()

        if not leads:
            raise HTTPException(status_code=404, detail="No valid leads found")

        # Filter eligible leads (pending or not recently called)
        eligible_leads = [
            lead for lead in leads
            if lead.status in [LeadStatus.PENDING, LeadStatus.NO_ANSWER]
        ]

        if not eligible_leads:
            raise HTTPException(
                status_code=400,
                detail="No eligible leads (must be pending or no_answer status)"
            )

        # Queue leads for calling (this will be handled by Celery in production)
        queued_count = 0
        for lead in eligible_leads:
            # Update status to queued
            lead.status = LeadStatus.QUEUED
            queued_count += 1

            # In production, queue Celery task here:
            # from backend.workers.tasks import initiate_call
            # initiate_call.delay(lead.id)

        db.commit()

        logger.info(f"Campaign '{campaign.name}' started with {queued_count} leads")

        return CampaignResponse(
            success=True,
            message=f"Campaign started successfully",
            queued_leads=queued_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start campaign: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_campaign_status(db: Session = Depends(get_db)):
    """Get current campaign status (queued, calling, etc.)"""
    try:
        # Count leads by status
        from sqlalchemy import func

        status_counts = db.query(
            Lead.status,
            func.count(Lead.id).label('count')
        ).group_by(Lead.status).all()

        return {
            "status_counts": {
                status.value: count for status, count in status_counts
            }
        }

    except Exception as e:
        logger.error(f"Failed to get campaign status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
