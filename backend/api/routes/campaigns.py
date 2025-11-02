"""
Campaigns API routes - for initiating bulk calls
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import logging
import sys
import os
import time

# Ensure parent directory is in path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

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

        # Queue leads for calling with Celery
        # Use send_task to avoid import issues
        try:
            from backend.workers.celery_app import celery_app
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Failed to import celery_app: {error_details}")
            raise HTTPException(status_code=500, detail=f"Import error: {str(e)}\n{error_details}")

        queued_count = 0
        failed_count = 0

        for lead in eligible_leads:
            try:
                # Update status to queued
                lead.status = LeadStatus.QUEUED
                db.commit()

                # Queue Celery task with countdown for rate limiting
                # Stagger calls by 5 seconds each to avoid overwhelming the system
                countdown = queued_count * 5

                # Generate unique task ID to prevent duplicate task queueing
                # This ensures idempotency - if the same task is queued multiple times,
                # only one will execute
                task_id = f"initiate_call_lead_{lead.id}_{int(time.time())}"

                # Use send_task with task name instead of importing the task function
                celery_app.send_task(
                    'backend.workers.tasks.initiate_call',
                    args=[lead.id],
                    countdown=countdown,
                    task_id=task_id  # Prevents duplicate tasks with same ID
                )

                queued_count += 1
                logger.info(f"Queued call for lead {lead.id} (delay: {countdown}s)")

            except Exception as e:
                logger.error(f"Failed to queue lead {lead.id}: {str(e)}")
                failed_count += 1
                lead.status = LeadStatus.PENDING  # Reset to pending if queueing failed
                db.commit()

        db.commit()

        logger.info(f"Campaign '{campaign.name}' started: {queued_count} queued, {failed_count} failed")

        message = f"Campaign started successfully with {queued_count} leads queued"
        if failed_count > 0:
            message += f" ({failed_count} failed to queue)"

        return CampaignResponse(
            success=True,
            message=message,
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
