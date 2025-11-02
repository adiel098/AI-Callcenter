"""
Google Calendar integration service for meeting scheduling
Supports both OAuth (development) and Service Account (production) authentication
"""
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
from pathlib import Path
import pickle
import os

from backend.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Scopes required for calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarService:
    """
    Service for Google Calendar operations

    Supports two authentication modes:
    1. OAuth (Development): Uses credentials.json + token.json with browser auth
    2. Service Account (Production): Uses service-account.json for headless auth
    """

    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """
        Authenticate with Google Calendar API

        Priority:
        1. Service Account (if service-account.json exists) - Production
        2. OAuth Token (if token.json exists) - Development
        3. OAuth Flow (if credentials.json exists) - First-time setup
        """
        # Check for service account credentials (Production)
        service_account_path = Path('backend/service-account.json')
        if service_account_path.exists():
            logger.info("Using Service Account authentication (Production mode)")
            try:
                self.creds = service_account.Credentials.from_service_account_file(
                    str(service_account_path),
                    scopes=SCOPES
                )
                logger.info("✅ Service Account authentication successful")
            except Exception as e:
                logger.error(f"❌ Service Account authentication failed: {str(e)}")
                return
        else:
            # OAuth authentication (Development)
            logger.info("Using OAuth authentication (Development mode)")
            token_path = Path(settings.google_calendar_token_file)
            creds_path = Path(settings.google_calendar_credentials_file)

            # Load existing token
            if token_path.exists():
                try:
                    with open(token_path, 'rb') as token:
                        self.creds = pickle.load(token)
                except Exception as e:
                    logger.warning(f"Failed to load token: {e}")
                    self.creds = None

            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        self.creds.refresh(Request())
                        logger.info("Google Calendar credentials refreshed")
                    except Exception as e:
                        logger.error(f"Failed to refresh credentials: {str(e)}")
                        self.creds = None

                # If still no valid creds, need to authenticate
                if not self.creds and creds_path.exists():
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(creds_path), SCOPES
                        )
                        self.creds = flow.run_local_server(port=0)
                        logger.info("New Google Calendar credentials obtained")
                    except Exception as e:
                        logger.error(f"Failed to obtain credentials: {str(e)}")
                        return

                # Save credentials
                if self.creds:
                    with open(token_path, 'wb') as token:
                        pickle.dump(self.creds, token)

        # Build service
        if self.creds:
            try:
                self.service = build('calendar', 'v3', credentials=self.creds)
                logger.info("✅ Google Calendar service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to build calendar service: {str(e)}")

    def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 30,
        calendar_id: str = None
    ) -> List[Dict]:
        """
        Get available time slots in calendar

        Args:
            start_date: Start of search range
            end_date: End of search range
            duration_minutes: Meeting duration
            calendar_id: Calendar ID (uses default if None)

        Returns:
            List of available slots with start/end times
        """
        if not self.service:
            logger.error("Calendar service not initialized")
            return []

        calendar_id = calendar_id or settings.google_calendar_id or 'primary'

        try:
            # Get busy times
            body = {
                "timeMin": start_date.isoformat() + 'Z',
                "timeMax": end_date.isoformat() + 'Z',
                "items": [{"id": calendar_id}]
            }

            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result['calendars'][calendar_id]['busy']

            # Generate available slots
            available_slots = []
            current_time = start_date

            # Define working hours (9 AM - 5 PM)
            while current_time < end_date:
                # Skip non-working hours
                if current_time.hour < 9 or current_time.hour >= 17:
                    current_time += timedelta(hours=1)
                    continue

                slot_end = current_time + timedelta(minutes=duration_minutes)

                # Check if slot overlaps with busy time
                is_available = True
                for busy in busy_times:
                    busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))

                    if (current_time < busy_end and slot_end > busy_start):
                        is_available = False
                        current_time = busy_end
                        break

                if is_available:
                    available_slots.append({
                        "start": current_time.isoformat(),
                        "end": slot_end.isoformat(),
                        "display": current_time.strftime("%A, %B %d at %I:%M %p")
                    })

                current_time += timedelta(minutes=30)  # Check every 30 minutes

            logger.info(f"Found {len(available_slots)} available slots")
            return available_slots[:10]  # Return first 10 slots

        except HttpError as error:
            logger.error(f"Calendar API error: {error}")
            return []

    def create_meeting(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        attendee_email: str,
        description: str = "",
        calendar_id: str = None
    ) -> Optional[dict]:
        """
        Create a meeting event in calendar

        Args:
            summary: Meeting title
            start_time: Meeting start time
            end_time: Meeting end time
            attendee_email: Guest email address (not added to calendar, used for invite email)
            description: Meeting description
            calendar_id: Calendar ID (uses default if None)

        Returns:
            dict with event_id and google_meet_link if successful, None otherwise
            Example: {'event_id': 'abc123', 'google_meet_link': 'https://meet.google.com/xxx-yyyy-zzz'}
        """
        if not self.service:
            logger.error("Calendar service not initialized")
            return None

        calendar_id = calendar_id or settings.google_calendar_id or 'primary'

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            # NOTE: 'attendees' field removed to avoid forbiddenForServiceAccounts error
            # Calendar invites are now sent via EmailService with .ics attachments
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meeting-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        try:
            event_result = self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='none'  # Changed from 'all' - invites sent via email service
            ).execute()

            event_id = event_result['id']

            # Extract Google Meet link if available
            google_meet_link = None
            if 'conferenceData' in event_result and 'entryPoints' in event_result['conferenceData']:
                for entry_point in event_result['conferenceData']['entryPoints']:
                    if entry_point.get('entryPointType') == 'video':
                        google_meet_link = entry_point.get('uri')
                        break

            logger.info(f"Meeting created: {event_id} at {start_time}, Meet link: {google_meet_link}")

            return {
                'event_id': event_id,
                'google_meet_link': google_meet_link
            }

        except HttpError as error:
            logger.error(f"Failed to create meeting: {error}")
            return None

    def update_meeting(
        self,
        event_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        attendee_email: Optional[str] = None,
        calendar_id: str = None
    ) -> bool:
        """
        Update an existing meeting

        Args:
            event_id: Event ID to update
            start_time: New start time (optional)
            end_time: New end time (optional)
            attendee_email: New attendee email (optional)
            calendar_id: Calendar ID

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        calendar_id = calendar_id or settings.google_calendar_id or 'primary'

        try:
            # Get existing event
            event = self.service.events().get(calendarId=calendar_id, eventId=event_id).execute()

            # Update fields
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
            if end_time:
                event['end']['dateTime'] = end_time.isoformat()
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]

            # Update event
            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            logger.info(f"Meeting updated: {event_id}")
            return True

        except HttpError as error:
            logger.error(f"Failed to update meeting: {error}")
            return False

    def cancel_meeting(self, event_id: str, calendar_id: str = None) -> bool:
        """
        Cancel a meeting

        Args:
            event_id: Event ID to cancel
            calendar_id: Calendar ID

        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            return False

        calendar_id = calendar_id or settings.google_calendar_id or 'primary'

        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()

            logger.info(f"Meeting cancelled: {event_id}")
            return True

        except HttpError as error:
            logger.error(f"Failed to cancel meeting: {error}")
            return False

    def get_next_available_slots(self, count: int = 5, duration_minutes: int = 30) -> List[Dict]:
        """
        Get next available slots starting from tomorrow

        Args:
            count: Number of slots to return
            duration_minutes: Meeting duration

        Returns:
            List of available slots
        """
        start_date = datetime.utcnow() + timedelta(days=1)
        start_date = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=14)  # Look 2 weeks ahead

        all_slots = self.get_available_slots(start_date, end_date, duration_minutes)
        return all_slots[:count]
