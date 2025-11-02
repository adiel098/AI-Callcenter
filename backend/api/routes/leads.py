"""
Leads API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr
import csv
import io
import logging

from backend.database import get_db
from backend.models import Lead, LeadStatus
from backend.utils.language_detector import detect_language_from_phone

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic schemas
class LeadCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None


class LeadResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    country_code: str | None
    language: str | None
    status: str
    created_at: str

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    page_size: int


@router.post("/", response_model=LeadResponse)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    """Create a new lead"""
    try:
        # Detect language from phone
        language, country_code = detect_language_from_phone(lead.phone)

        # Create lead
        db_lead = Lead(
            name=lead.name,
            phone=lead.phone,
            email=lead.email,
            country_code=country_code,
            language=language,
            status=LeadStatus.PENDING
        )

        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)

        logger.info(f"Lead created: {db_lead.id} - {db_lead.name}")

        return LeadResponse(
            id=db_lead.id,
            name=db_lead.name,
            phone=db_lead.phone,
            email=db_lead.email,
            country_code=db_lead.country_code,
            language=db_lead.language,
            status=db_lead.status.value,
            created_at=db_lead.created_at.isoformat()
        )

    except Exception as e:
        logger.error(f"Failed to create lead: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=LeadListResponse)
async def get_leads(
    page: int = 1,
    page_size: int = 50,
    status: str | None = None,
    db: Session = Depends(get_db)
):
    """Get list of leads with pagination"""
    try:
        query = db.query(Lead)

        # Filter by status if provided
        if status:
            query = query.filter(Lead.status == status)

        # Get total count
        total = query.count()

        # Paginate
        leads = query.offset((page - 1) * page_size).limit(page_size).all()

        return LeadListResponse(
            leads=[
                LeadResponse(
                    id=lead.id,
                    name=lead.name,
                    phone=lead.phone,
                    email=lead.email,
                    country_code=lead.country_code,
                    language=lead.language,
                    status=lead.status.value,
                    created_at=lead.created_at.isoformat()
                )
                for lead in leads
            ],
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Failed to get leads: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead by ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return LeadResponse(
        id=lead.id,
        name=lead.name,
        phone=lead.phone,
        email=lead.email,
        country_code=lead.country_code,
        language=lead.language,
        status=lead.status.value,
        created_at=lead.created_at.isoformat()
    )


@router.post("/upload")
async def upload_leads_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload leads from CSV file

    CSV format: name,phone,email
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read CSV content
        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        csv_reader = csv.DictReader(csv_file)

        leads_created = 0
        errors = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Validate required fields
                if 'name' not in row or 'phone' not in row:
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue

                name = row['name'].strip()
                phone = row['phone'].strip()
                email = row.get('email', '').strip() or None

                # Detect language
                language, country_code = detect_language_from_phone(phone)

                # Check if lead already exists
                existing = db.query(Lead).filter(Lead.phone == phone).first()
                if existing:
                    errors.append(f"Row {row_num}: Phone {phone} already exists")
                    continue

                # Create lead
                lead = Lead(
                    name=name,
                    phone=phone,
                    email=email,
                    country_code=country_code,
                    language=language,
                    status=LeadStatus.PENDING
                )

                db.add(lead)
                leads_created += 1

            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue

        # Commit all leads
        db.commit()

        logger.info(f"Uploaded {leads_created} leads from CSV")

        return {
            "success": True,
            "leads_created": leads_created,
            "errors": errors if errors else None
        }

    except Exception as e:
        logger.error(f"Failed to upload CSV: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()

    logger.info(f"Lead deleted: {lead_id}")

    return {"success": True, "message": "Lead deleted"}
