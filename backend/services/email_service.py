"""
Email Service for sending calendar invites and notifications.

This service handles:
- Sending calendar invites as .ics attachments
- SMTP email delivery
- Support for all email providers (Gmail, Outlook, Yahoo, corporate)
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import Optional
from icalendar import Calendar, Event as ICSEvent
from icalendar import vCalAddress, vText

from backend.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails with calendar invites.

    Supports sending .ics calendar files as email attachments,
    which works with all email providers (Gmail, Outlook, Yahoo, etc.)
    """

    def __init__(self):
        """Initialize email service with SMTP configuration."""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_user
        self.from_name = settings.company_name

        logger.info("Email service initialized")

    def send_calendar_invite(
        self,
        attendee_email: str,
        attendee_name: str,
        meeting_datetime: datetime,
        duration_minutes: int = 30,
        meeting_title: str = "Meeting",
        meeting_description: str = "",
        location: str = "",
        google_meet_link: str = None
    ) -> bool:
        """
        Send calendar invite as .ics email attachment.

        Args:
            attendee_email: Recipient's email address
            attendee_name: Recipient's name
            meeting_datetime: Start time of meeting (timezone-aware)
            duration_minutes: Meeting duration in minutes
            meeting_title: Meeting subject/title
            meeting_description: Meeting description
            location: Meeting location (or "Google Meet" for virtual)
            google_meet_link: Optional Google Meet link

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create .ics calendar file
            ics_content = self._create_ics_file(
                attendee_email=attendee_email,
                attendee_name=attendee_name,
                meeting_datetime=meeting_datetime,
                duration_minutes=duration_minutes,
                meeting_title=meeting_title,
                meeting_description=meeting_description,
                location=location,
                google_meet_link=google_meet_link
            )

            # Create email with .ics attachment
            msg = self._create_email_with_ics(
                to_email=attendee_email,
                to_name=attendee_name,
                meeting_datetime=meeting_datetime,
                duration_minutes=duration_minutes,
                meeting_title=meeting_title,
                meeting_description=meeting_description,
                location=location,
                google_meet_link=google_meet_link,
                ics_content=ics_content
            )

            # Send email via SMTP
            self._send_email(msg)

            logger.info(f"Calendar invite sent successfully to {attendee_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send calendar invite to {attendee_email}: {e}")
            return False

    def _create_ics_file(
        self,
        attendee_email: str,
        attendee_name: str,
        meeting_datetime: datetime,
        duration_minutes: int,
        meeting_title: str,
        meeting_description: str,
        location: str,
        google_meet_link: str = None
    ) -> bytes:
        """
        Create .ics calendar file content.

        Returns:
            bytes: .ics file content
        """
        # Create calendar
        cal = Calendar()
        cal.add('prodid', f'-//{self.from_name}//Meeting Scheduler//EN')
        cal.add('version', '2.0')
        cal.add('method', 'REQUEST')

        # Create event
        event = ICSEvent()
        event.add('summary', meeting_title)
        event.add('dtstart', meeting_datetime)
        event.add('dtend', meeting_datetime + timedelta(minutes=duration_minutes))
        event.add('dtstamp', datetime.now())

        # Add organizer
        organizer = vCalAddress(f'MAILTO:{self.from_email}')
        organizer.params['cn'] = vText(self.from_name)
        organizer.params['role'] = vText('CHAIR')
        event['organizer'] = organizer

        # Add attendee
        attendee = vCalAddress(f'MAILTO:{attendee_email}')
        attendee.params['cn'] = vText(attendee_name)
        attendee.params['role'] = vText('REQ-PARTICIPANT')
        attendee.params['partstat'] = vText('NEEDS-ACTION')
        attendee.params['rsvp'] = vText('TRUE')
        event.add('attendee', attendee, encode=0)

        # Add description
        full_description = meeting_description
        if google_meet_link:
            full_description += f"\n\nJoin meeting: {google_meet_link}"
        if full_description:
            event.add('description', full_description)

        # Add location
        if google_meet_link:
            event.add('location', 'Google Meet')
            event.add('url', google_meet_link)
        elif location:
            event.add('location', location)

        # Add status and class
        event.add('status', 'CONFIRMED')
        event.add('sequence', 0)
        event.add('priority', 5)

        # Add UID for calendar systems
        uid = f"{meeting_datetime.timestamp()}@{self.from_email}"
        event.add('uid', uid)

        # Add event to calendar
        cal.add_component(event)

        return cal.to_ical()

    def _create_email_with_ics(
        self,
        to_email: str,
        to_name: str,
        meeting_datetime: datetime,
        duration_minutes: int,
        meeting_title: str,
        meeting_description: str,
        location: str,
        google_meet_link: str,
        ics_content: bytes
    ) -> MIMEMultipart:
        """
        Create email message with .ics attachment.

        Returns:
            MIMEMultipart: Email message object
        """
        # Create message
        msg = MIMEMultipart('mixed')
        msg['From'] = f'{self.from_name} <{self.from_email}>'
        msg['To'] = f'{to_name} <{to_email}>'
        msg['Subject'] = f'Meeting Invitation: {meeting_title}'

        # Create HTML and plain text versions
        text_body = self._create_email_body_text(
            to_name=to_name,
            meeting_datetime=meeting_datetime,
            duration_minutes=duration_minutes,
            meeting_title=meeting_title,
            meeting_description=meeting_description,
            location=location,
            google_meet_link=google_meet_link
        )

        html_body = self._create_email_body_html(
            to_name=to_name,
            meeting_datetime=meeting_datetime,
            duration_minutes=duration_minutes,
            meeting_title=meeting_title,
            meeting_description=meeting_description,
            location=location,
            google_meet_link=google_meet_link
        )

        # Create alternative part for text and HTML
        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)

        msg_alternative.attach(MIMEText(text_body, 'plain'))
        msg_alternative.attach(MIMEText(html_body, 'html'))

        # Attach .ics file
        ics_part = MIMEBase('text', 'calendar', method='REQUEST', name='invite.ics')
        ics_part.set_payload(ics_content)
        encoders.encode_base64(ics_part)
        ics_part.add_header('Content-Disposition', 'attachment', filename='invite.ics')
        ics_part.add_header('Content-class', 'urn:content-classes:calendarmessage')
        msg.attach(ics_part)

        return msg

    def _create_email_body_text(
        self,
        to_name: str,
        meeting_datetime: datetime,
        duration_minutes: int,
        meeting_title: str,
        meeting_description: str,
        location: str,
        google_meet_link: str
    ) -> str:
        """Create plain text email body."""
        end_time = meeting_datetime + timedelta(minutes=duration_minutes)

        body = f"""Hi {to_name},

Your meeting has been scheduled!

Meeting Details:
Title: {meeting_title}
Date: {meeting_datetime.strftime('%A, %B %d, %Y')}
Time: {meeting_datetime.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
Duration: {duration_minutes} minutes
"""

        if google_meet_link:
            body += f"\nJoin via Google Meet: {google_meet_link}\n"
        elif location:
            body += f"\nLocation: {location}\n"

        if meeting_description:
            body += f"\nDescription:\n{meeting_description}\n"

        body += """
To add this meeting to your calendar, open the attached invite.ics file.

Looking forward to speaking with you!

Best regards,
""" + self.from_name

        return body

    def _create_email_body_html(
        self,
        to_name: str,
        meeting_datetime: datetime,
        duration_minutes: int,
        meeting_title: str,
        meeting_description: str,
        location: str,
        google_meet_link: str
    ) -> str:
        """Create HTML email body."""
        end_time = meeting_datetime + timedelta(minutes=duration_minutes)

        location_html = ""
        if google_meet_link:
            location_html = f'<p><strong>Join via:</strong> <a href="{google_meet_link}">Google Meet</a></p>'
        elif location:
            location_html = f'<p><strong>Location:</strong> {location}</p>'

        description_html = ""
        if meeting_description:
            description_html = f'<p><strong>Description:</strong><br>{meeting_description.replace(chr(10), "<br>")}</p>'

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4285f4; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
        .meeting-details {{ background-color: white; padding: 20px; border-left: 4px solid #4285f4; margin: 20px 0; }}
        .meeting-details p {{ margin: 10px 0; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #4285f4; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Meeting Invitation</h1>
        </div>
        <div class="content">
            <p>Hi {to_name},</p>
            <p>Your meeting has been scheduled!</p>

            <div class="meeting-details">
                <h2 style="margin-top: 0;">{meeting_title}</h2>
                <p><strong>Date:</strong> {meeting_datetime.strftime('%A, %B %d, %Y')}</p>
                <p><strong>Time:</strong> {meeting_datetime.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}</p>
                <p><strong>Duration:</strong> {duration_minutes} minutes</p>
                {location_html}
                {description_html}
            </div>

            <p>To add this meeting to your calendar, open the attached <strong>invite.ics</strong> file or click "Add to Calendar" in your email client.</p>

            <p>Looking forward to speaking with you!</p>

            <p>Best regards,<br>{self.from_name}</p>

            <div class="footer">
                <p>This is an automated message from {self.from_name}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _send_email(self, msg: MIMEMultipart) -> None:
        """
        Send email via SMTP.

        Args:
            msg: Email message to send

        Raises:
            Exception: If SMTP send fails
        """
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully via {self.smtp_host}")

        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            raise

    def send_meeting_confirmation(
        self,
        attendee_email: str,
        attendee_name: str,
        meeting_datetime: datetime,
        meeting_title: str
    ) -> bool:
        """
        Send simple meeting confirmation email (without .ics file).

        Useful for confirmations after the invite has already been sent.

        Args:
            attendee_email: Recipient's email
            attendee_name: Recipient's name
            meeting_datetime: Meeting start time
            meeting_title: Meeting subject

        Returns:
            bool: True if sent successfully
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = f'{attendee_name} <{attendee_email}>'
            msg['Subject'] = f'Meeting Confirmation: {meeting_title}'

            body = f"""Hi {attendee_name},

This is a confirmation that your meeting has been scheduled:

Title: {meeting_title}
Date/Time: {meeting_datetime.strftime('%A, %B %d, %Y at %I:%M %p')}

You should receive a separate calendar invitation shortly.

Best regards,
{self.from_name}
"""

            msg.attach(MIMEText(body, 'plain'))
            self._send_email(msg)

            logger.info(f"Confirmation email sent to {attendee_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send confirmation to {attendee_email}: {e}")
            return False
