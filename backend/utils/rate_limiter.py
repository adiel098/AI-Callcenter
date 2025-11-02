"""
Rate limiting utilities for API protection
"""
from fastapi import HTTPException
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter for API endpoints.

    Tracks request counts per partner within a time window.
    For production, consider using Redis-based rate limiting.

    Attributes:
        requests: Dict mapping partner_id to (count, window_start)
        window_seconds: Duration of rate limit window in seconds
    """

    def __init__(self, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            window_seconds: Rate limit window duration (default 60 seconds)
        """
        self.requests: Dict[int, Tuple[int, datetime]] = {}
        self.window_seconds = window_seconds

    def check_rate_limit(self, partner_id: int, limit: int) -> None:
        """
        Check if partner has exceeded rate limit.

        Args:
            partner_id: Partner ID to check
            limit: Maximum requests allowed in window

        Raises:
            HTTPException: 429 if rate limit exceeded
        """
        now = datetime.utcnow()

        # Get current count and window start for this partner
        if partner_id in self.requests:
            count, window_start = self.requests[partner_id]

            # Check if we're still in the same window
            if now - window_start < timedelta(seconds=self.window_seconds):
                # Same window - increment count
                if count >= limit:
                    logger.warning(
                        f"Rate limit exceeded for partner {partner_id}: "
                        f"{count} requests in {self.window_seconds}s window (limit: {limit})"
                    )
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Maximum {limit} requests per {self.window_seconds} seconds."
                    )

                # Increment count
                self.requests[partner_id] = (count + 1, window_start)
            else:
                # New window - reset count
                self.requests[partner_id] = (1, now)
        else:
            # First request from this partner
            self.requests[partner_id] = (1, now)

        logger.debug(f"Rate limit check passed for partner {partner_id}")

    def cleanup_old_entries(self) -> None:
        """
        Remove expired rate limit entries.

        Should be called periodically to prevent memory buildup.
        """
        now = datetime.utcnow()
        expired_partners = [
            partner_id
            for partner_id, (_, window_start) in self.requests.items()
            if now - window_start > timedelta(seconds=self.window_seconds * 2)
        ]

        for partner_id in expired_partners:
            del self.requests[partner_id]

        if expired_partners:
            logger.debug(f"Cleaned up {len(expired_partners)} expired rate limit entries")


# Global rate limiter instance
# Note: For production with multiple workers, use Redis-based rate limiting
rate_limiter = RateLimiter(window_seconds=60)
