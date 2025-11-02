"""
Authentication utilities for API access control
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import logging

from ..database import get_db
from ..models.partner import Partner

logger = logging.getLogger(__name__)


async def verify_api_key(
    x_api_key: Annotated[str, Header(description="Partner API key for authentication")],
    db: Session = Depends(get_db)
) -> Partner:
    """
    Verify API key and return associated partner.

    This dependency should be used on protected endpoints that require
    partner authentication.

    Args:
        x_api_key: API key from X-API-Key header
        db: Database session

    Returns:
        Partner: The authenticated partner object

    Raises:
        HTTPException: 401 if API key is missing, invalid, or partner is inactive
    """
    if not x_api_key:
        logger.warning("API request without API key")
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include 'X-API-Key' header."
        )

    # Look up partner by API key
    partner = db.query(Partner).filter(Partner.api_key == x_api_key).first()

    if not partner:
        logger.warning(f"Invalid API key attempted: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    if not partner.is_active:
        logger.warning(f"Inactive partner attempted access: {partner.name} (ID: {partner.id})")
        raise HTTPException(
            status_code=403,
            detail="Partner access has been disabled. Contact support."
        )

    logger.info(f"Successful authentication: Partner '{partner.name}' (ID: {partner.id})")
    return partner


async def verify_api_key_optional(
    x_api_key: Annotated[Optional[str], Header(description="Optional partner API key")] = None,
    db: Session = Depends(get_db)
) -> Optional[Partner]:
    """
    Optional API key verification.

    Returns partner if valid API key provided, otherwise None.
    Does not raise exceptions.

    Args:
        x_api_key: Optional API key from X-API-Key header
        db: Database session

    Returns:
        Partner or None: The authenticated partner if valid key provided, else None
    """
    if not x_api_key:
        return None

    try:
        partner = db.query(Partner).filter(
            Partner.api_key == x_api_key,
            Partner.is_active == True
        ).first()
        return partner
    except Exception as e:
        logger.error(f"Error in optional API key verification: {str(e)}")
        return None
