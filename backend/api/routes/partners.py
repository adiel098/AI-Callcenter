"""
Partners API routes - Admin endpoints for managing API partners
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from backend.database import get_db
from backend.models import Partner, Lead
from backend.utils.auth import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class PartnerCreate(BaseModel):
    """Schema for creating a new partner"""
    name: str
    rate_limit: Optional[int] = 100  # Default 100 leads per minute


class PartnerUpdate(BaseModel):
    """Schema for updating partner details"""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    rate_limit: Optional[int] = None


class PartnerResponse(BaseModel):
    """Schema for partner response (without API key)"""
    id: int
    name: str
    is_active: bool
    rate_limit: int
    created_at: datetime
    updated_at: datetime
    total_leads: Optional[int] = 0

    class Config:
        from_attributes = True


class PartnerWithKeyResponse(BaseModel):
    """Schema for partner response including API key (only on creation)"""
    id: int
    name: str
    api_key: str
    is_active: bool
    rate_limit: int
    created_at: datetime

    class Config:
        from_attributes = True


class PartnerListResponse(BaseModel):
    """Schema for paginated partner list"""
    partners: List[PartnerResponse]
    total: int


# Admin endpoints (TODO: Add admin authentication)
@router.post("/", response_model=PartnerWithKeyResponse, status_code=201)
async def create_partner(
    partner_data: PartnerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new API partner.

    This endpoint generates a unique API key for the partner.
    **IMPORTANT**: The API key is only shown once during creation.
    Store it securely as it cannot be retrieved later.

    Args:
        partner_data: Partner creation data (name, rate_limit)
        db: Database session

    Returns:
        PartnerWithKeyResponse: Created partner with API key

    Raises:
        HTTPException: 400 if partner name already exists
    """
    try:
        # Check if partner name already exists
        existing = db.query(Partner).filter(Partner.name == partner_data.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Partner with name '{partner_data.name}' already exists"
            )

        # Generate API key
        api_key = Partner.generate_api_key()

        # Create partner
        partner = Partner(
            name=partner_data.name,
            api_key=api_key,
            rate_limit=partner_data.rate_limit,
            is_active=True
        )

        db.add(partner)
        db.commit()
        db.refresh(partner)

        logger.info(f"Created new partner: {partner.name} (ID: {partner.id})")

        return PartnerWithKeyResponse(
            id=partner.id,
            name=partner.name,
            api_key=api_key,  # Only shown on creation
            is_active=partner.is_active,
            rate_limit=partner.rate_limit,
            created_at=partner.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating partner: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=PartnerListResponse)
async def list_partners(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    List all API partners.

    Args:
        active_only: If True, only return active partners
        db: Database session

    Returns:
        PartnerListResponse: List of partners with lead counts
    """
    try:
        query = db.query(Partner)

        if active_only:
            query = query.filter(Partner.is_active == True)

        partners = query.order_by(Partner.created_at.desc()).all()

        # Add lead counts
        partner_responses = []
        for partner in partners:
            lead_count = db.query(Lead).filter(Lead.partner_id == partner.id).count()
            partner_dict = {
                "id": partner.id,
                "name": partner.name,
                "is_active": partner.is_active,
                "rate_limit": partner.rate_limit,
                "created_at": partner.created_at,
                "updated_at": partner.updated_at,
                "total_leads": lead_count
            }
            partner_responses.append(PartnerResponse(**partner_dict))

        return PartnerListResponse(
            partners=partner_responses,
            total=len(partner_responses)
        )

    except Exception as e:
        logger.error(f"Error listing partners: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{partner_id}", response_model=PartnerResponse)
async def get_partner(
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific partner by ID.

    Args:
        partner_id: Partner ID
        db: Database session

    Returns:
        PartnerResponse: Partner details with lead count

    Raises:
        HTTPException: 404 if partner not found
    """
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()

        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")

        # Get lead count
        lead_count = db.query(Lead).filter(Lead.partner_id == partner.id).count()

        partner_dict = {
            "id": partner.id,
            "name": partner.name,
            "is_active": partner.is_active,
            "rate_limit": partner.rate_limit,
            "created_at": partner.created_at,
            "updated_at": partner.updated_at,
            "total_leads": lead_count
        }

        return PartnerResponse(**partner_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting partner {partner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{partner_id}", response_model=PartnerResponse)
async def update_partner(
    partner_id: int,
    updates: PartnerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update partner details.

    Can update name, active status, or rate limit.

    Args:
        partner_id: Partner ID
        updates: Fields to update
        db: Database session

    Returns:
        PartnerResponse: Updated partner details

    Raises:
        HTTPException: 404 if partner not found
    """
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()

        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")

        # Update fields if provided
        if updates.name is not None:
            # Check name uniqueness
            existing = db.query(Partner).filter(
                Partner.name == updates.name,
                Partner.id != partner_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Partner with name '{updates.name}' already exists"
                )
            partner.name = updates.name

        if updates.is_active is not None:
            partner.is_active = updates.is_active
            logger.info(f"Partner {partner.name} (ID: {partner_id}) active status changed to: {updates.is_active}")

        if updates.rate_limit is not None:
            partner.rate_limit = updates.rate_limit

        db.commit()
        db.refresh(partner)

        # Get lead count
        lead_count = db.query(Lead).filter(Lead.partner_id == partner.id).count()

        partner_dict = {
            "id": partner.id,
            "name": partner.name,
            "is_active": partner.is_active,
            "rate_limit": partner.rate_limit,
            "created_at": partner.created_at,
            "updated_at": partner.updated_at,
            "total_leads": lead_count
        }

        return PartnerResponse(**partner_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating partner {partner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{partner_id}/regenerate-key", response_model=PartnerWithKeyResponse)
async def regenerate_api_key(
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Regenerate API key for a partner.

    **WARNING**: This will invalidate the old API key immediately.
    The new key is only shown once.

    Args:
        partner_id: Partner ID
        db: Database session

    Returns:
        PartnerWithKeyResponse: Partner with new API key

    Raises:
        HTTPException: 404 if partner not found
    """
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()

        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")

        # Generate new API key
        new_api_key = Partner.generate_api_key()
        partner.api_key = new_api_key

        db.commit()
        db.refresh(partner)

        logger.warning(f"API key regenerated for partner: {partner.name} (ID: {partner_id})")

        return PartnerWithKeyResponse(
            id=partner.id,
            name=partner.name,
            api_key=new_api_key,
            is_active=partner.is_active,
            rate_limit=partner.rate_limit,
            created_at=partner.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error regenerating API key for partner {partner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{partner_id}", status_code=204)
async def delete_partner(
    partner_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a partner.

    **WARNING**: This will also remove the partner_id association from all their leads.

    Args:
        partner_id: Partner ID
        db: Database session

    Raises:
        HTTPException: 404 if partner not found
    """
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()

        if not partner:
            raise HTTPException(status_code=404, detail="Partner not found")

        # Remove partner_id from associated leads (set to NULL)
        db.query(Lead).filter(Lead.partner_id == partner_id).update({"partner_id": None})

        # Delete partner
        db.delete(partner)
        db.commit()

        logger.info(f"Deleted partner: {partner.name} (ID: {partner_id})")

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting partner {partner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
