"""
Test booking a meeting with Zoom link
"""
import asyncio
from datetime import datetime, timedelta
from backend.services.calendar_service import CalendarService
from backend.services.zoom_service import ZoomService

async def test_booking_with_zoom():
    """Test booking a meeting with Zoom integration"""
    print("=" * 60)
    print("Testing Meeting Booking with Zoom Link")
    print("=" * 60)

    # Initialize services
    calendar_service = CalendarService()
    zoom_service = ZoomService()

    # Meeting details - November 5, 2025 at 2:00 PM UTC
    meeting_datetime = datetime(2025, 11, 5, 14, 0, 0)
    duration_minutes = 30
    meeting_title = "Alta AI Discovery Call"
    guest_email = "test@example.com"
    guest_name = "John Doe"
    meeting_description = "Discussing AI workforce solutions and revenue operations"

    print("\nMeeting Details:")
    print(f"  Date/Time: {meeting_datetime.strftime('%B %d, %Y at %I:%M %p')} UTC")
    print(f"  Guest: {guest_name} ({guest_email})")
    print(f"  Duration: {duration_minutes} minutes")
    print(f"  Title: {meeting_title}")

    # Step 1: Create Zoom meeting
    print("\n" + "=" * 60)
    print("Step 1: Creating Zoom Meeting")
    print("=" * 60)

    zoom_meeting = zoom_service.create_meeting(
        topic=meeting_title,
        start_time=meeting_datetime,
        duration=duration_minutes,
        agenda=meeting_description
    )

    if zoom_meeting:
        print(f"[OK] Zoom meeting created successfully!")
        print(f"  Join URL: {zoom_meeting['join_url']}")
        print(f"  Meeting ID: {zoom_meeting['meeting_id']}")
        print(f"  Password: {zoom_meeting['password']}")

        # Add Zoom link to description
        full_description = f"{meeting_description}\n\n"
        full_description += f"Join Zoom Meeting:\n{zoom_meeting['join_url']}\n"
        full_description += f"Meeting ID: {zoom_meeting['meeting_id']}\n"
        full_description += f"Password: {zoom_meeting['password']}"

    else:
        print("[ERROR] Failed to create Zoom meeting")
        print("  This is expected if Zoom credentials are not configured")
        print("  Continuing with calendar booking without Zoom link...")
        full_description = meeting_description
        zoom_meeting = None

    # Step 2: Create calendar event
    print("\n" + "=" * 60)
    print("Step 2: Creating Calendar Event")
    print("=" * 60)

    end_time = meeting_datetime + timedelta(minutes=duration_minutes)

    calendar_result = calendar_service.create_meeting(
        summary=meeting_title,
        start_time=meeting_datetime,
        end_time=end_time,
        attendee_email=guest_email,
        description=full_description
    )

    if calendar_result:
        print(f"[OK] Calendar event created successfully!")
        print(f"  Event ID: {calendar_result['event_id']}")
        print(f"  Google Meet Link: {calendar_result.get('google_meet_link', 'None')}")
    else:
        print("[ERROR] Failed to create calendar event")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if calendar_result and zoom_meeting:
        print("[SUCCESS] Meeting booked with Zoom link!")
        print(f"\nCalendar Event ID: {calendar_result['event_id']}")
        print(f"Zoom Join URL: {zoom_meeting['join_url']}")
        print(f"\nThe calendar event includes:")
        print(f"  - Meeting scheduled for {meeting_datetime.strftime('%B %d, %Y at %I:%M %p')} UTC")
        print(f"  - Zoom link in description")
        print(f"  - Meeting ID and password")
        print(f"\nNote: Guest invitation email NOT sent (attendees field removed)")
        print(f"      To send invites, configure EmailService or use Domain-Wide Delegation")

    elif calendar_result:
        print("[SUCCESS] Calendar event created (without Zoom)")
        print(f"Event ID: {calendar_result['event_id']}")
        print(f"\nTo enable Zoom links:")
        print(f"  1. Go to https://marketplace.zoom.us/")
        print(f"  2. Create Server-to-Server OAuth app")
        print(f"  3. Add credentials to .env file")
        print(f"  4. See ZOOM_SETUP.md for details")

    else:
        print("[FAILED] Calendar event creation failed")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_booking_with_zoom())
