"""
Zoom Meeting Service for creating video conference links
Simpler alternative to Google Meet - no delegation required
"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import base64
import json

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ZoomService:
    """
    Service for creating Zoom meetings via Zoom API

    Requires:
    - Zoom Account (free or paid)
    - Server-to-Server OAuth app in Zoom Marketplace
    - Account ID, Client ID, Client Secret
    """

    def __init__(self):
        """Initialize Zoom service with credentials"""
        self.account_id = getattr(settings, 'zoom_account_id', None)
        self.client_id = getattr(settings, 'zoom_client_id', None)
        self.client_secret = getattr(settings, 'zoom_client_secret', None)
        self.access_token = None

        if not all([self.account_id, self.client_id, self.client_secret]):
            logger.warning("Zoom credentials not configured - Zoom meetings disabled")
        else:
            logger.info("Zoom service initialized")

    def _get_access_token(self) -> Optional[str]:
        """
        Get OAuth access token using Server-to-Server OAuth

        Returns:
            Access token or None if failed
        """
        if not all([self.account_id, self.client_id, self.client_secret]):
            logger.error("Zoom credentials missing")
            return None

        try:
            # Zoom OAuth token endpoint
            url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={self.account_id}"

            # Create Basic Auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }

            response = requests.post(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get('access_token')

            logger.info("Zoom access token obtained")
            return self.access_token

        except Exception as e:
            logger.error(f"Failed to get Zoom access token: {e}")
            return None

    def create_meeting(
        self,
        topic: str = "Meeting",
        start_time: Optional[datetime] = None,
        duration: int = 30,
        timezone: str = "UTC",
        agenda: str = ""
    ) -> Optional[Dict]:
        """
        Create a Zoom meeting

        Args:
            topic: Meeting title
            start_time: Meeting start time (None for instant meeting)
            duration: Duration in minutes
            timezone: Timezone for the meeting
            agenda: Meeting description/agenda

        Returns:
            Dict with join_url, meeting_id, password or None if failed
            Example: {
                'join_url': 'https://zoom.us/j/123456789?pwd=xxx',
                'meeting_id': '123456789',
                'password': 'abc123'
            }
        """
        # Get fresh access token
        if not self._get_access_token():
            return None

        try:
            # Zoom Create Meeting API endpoint
            # Use 'me' as userId for the authenticated user
            url = "https://api.zoom.us/v2/users/me/meetings"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # Meeting payload
            payload = {
                "topic": topic,
                "type": 2,  # Scheduled meeting (1 = instant, 2 = scheduled)
                "duration": duration,
                "timezone": timezone,
                "agenda": agenda,
                "settings": {
                    "host_video": True,
                    "participant_video": True,
                    "join_before_host": True,
                    "mute_upon_entry": False,
                    "watermark": False,
                    "audio": "both",
                    "auto_recording": "none"
                }
            }

            # Add start_time if provided
            if start_time:
                # Format: 2025-11-03T10:00:00Z
                payload["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            meeting_data = response.json()

            result = {
                'join_url': meeting_data.get('join_url'),
                'meeting_id': str(meeting_data.get('id')),
                'password': meeting_data.get('password'),
                'start_url': meeting_data.get('start_url')  # Host start link
            }

            logger.info(f"Zoom meeting created: {result['meeting_id']}")
            logger.info(f"Join URL: {result['join_url']}")

            return result

        except requests.exceptions.HTTPError as e:
            logger.error(f"Zoom API HTTP error: {e}")
            logger.error(f"Response: {e.response.text if e.response else 'No response'}")
            return None
        except Exception as e:
            logger.error(f"Failed to create Zoom meeting: {e}")
            return None

    def delete_meeting(self, meeting_id: str) -> bool:
        """
        Delete a Zoom meeting

        Args:
            meeting_id: Zoom meeting ID

        Returns:
            True if deleted successfully
        """
        if not self._get_access_token():
            return False

        try:
            url = f"https://api.zoom.us/v2/meetings/{meeting_id}"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            logger.info(f"Zoom meeting deleted: {meeting_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Zoom meeting {meeting_id}: {e}")
            return False
