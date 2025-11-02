"""
Test LLM service booking with Zoom integration
Tests the complete flow: LLM → book_meeting tool → Zoom link creation
"""
import asyncio
from datetime import datetime, timedelta
from backend.services.llm_service import LLMService
from backend.services.calendar_service import CalendarService
from backend.services.zoom_service import ZoomService


async def test_booking_with_zoom():
    """Test complete booking flow with Zoom integration"""

    print("=" * 80)
    print("TESTING: LLM Book Meeting Tool with Zoom Integration")
    print("=" * 80)
    print()

    # Initialize services
    print("1. Initializing services...")
    calendar_service = CalendarService()
    zoom_service = ZoomService()
    llm_service = LLMService(
        calendar_service=calendar_service,
        zoom_service=zoom_service
    )
    print("   Services initialized")
    print()

    # Simulate a conversation where user wants to book a meeting
    print("2. Simulating conversation...")
    lead_info = {
        "name": "John Doe",
        "email": "haleviadiel@gmail.com",  # Your test email
        "company": "Test Company"
    }

    conversation_history = [
        {"role": "assistant", "content": "Hi John, this is Alex from Alta AI. How are you?"},
        {"role": "user", "content": "Good! I'm interested in learning more about Alta."},
        {"role": "assistant", "content": "Great! Would you like to schedule a 30-minute discovery call?"},
        {"role": "user", "content": "Yes, that sounds good. When are you available?"},
    ]

    print("   Conversation so far:")
    for msg in conversation_history[-2:]:
        print(f"   {msg['role']}: {msg['content']}")
    print()

    # Get AI response with tools (should check calendar)
    print("3. AI checking calendar availability...")
    user_message = "How about next Tuesday?"
    intent, response, tools_used = await llm_service.get_response_with_tools(
        user_message=user_message,
        conversation_history=conversation_history,
        lead_info=lead_info
    )

    print(f"   User: {user_message}")
    print(f"   AI Intent: {intent}")
    print(f"   AI Response: {response}")
    if tools_used:
        print(f"   Tools used: {len(tools_used)}")
        for tool in tools_used:
            print(f"      - {tool['tool']}: {tool['result'].get('success', False)}")
    print()

    # User confirms time and provides email
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": response})

    print("4. User confirms meeting time...")
    # Calculate next Tuesday at 2:00 PM
    today = datetime.utcnow()
    days_ahead = (1 - today.weekday()) % 7  # Tuesday is 1
    if days_ahead == 0:
        days_ahead = 7  # Next Tuesday
    next_tuesday = today + timedelta(days=days_ahead)
    next_tuesday = next_tuesday.replace(hour=14, minute=0, second=0, microsecond=0)

    user_confirms = f"Tuesday at 2pm works perfectly. My email is {lead_info['email']}"

    print(f"   User: {user_confirms}")
    print()

    # Get AI response (should book meeting with Zoom)
    print("5. AI booking meeting with Zoom link...")
    print("   This will:")
    print("      a) Create Zoom meeting")
    print("      b) Create Google Calendar event")
    print("      c) Include Zoom link in calendar description")
    print()

    intent, response, tools_used = await llm_service.get_response_with_tools(
        user_message=user_confirms,
        conversation_history=conversation_history,
        lead_info=lead_info
    )

    print(f"   AI Intent: {intent}")
    print(f"   AI Response: {response}")
    print()

    # Display booking results
    if tools_used:
        print("6. BOOKING RESULTS:")
        print("=" * 80)
        for tool in tools_used:
            if tool['tool'] == 'book_meeting':
                result = tool['result']
                if result.get('success'):
                    print("   MEETING BOOKED SUCCESSFULLY!")
                    print()
                    print(f"   Event ID: {result.get('event_id')}")
                    print(f"   Zoom Link: {result.get('zoom_link', 'N/A')}")
                    print(f"   Video Link: {result.get('video_link', 'N/A')}")
                    print(f"   Invite sent to: {lead_info['email']}")
                    print(f"   Message: {result.get('message')}")
                    print()

                    if result.get('zoom_link'):
                        print("   ZOOM INTEGRATION WORKING!")
                        print(f"      Join URL: {result['zoom_link']}")
                    else:
                        print("   NO ZOOM LINK GENERATED")
                        print("      Check:")
                        print("      - Zoom credentials in .env file")
                        print("      - ZoomService initialization logs")
                        print("      - ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET")
                else:
                    print("   BOOKING FAILED")
                    print(f"   Error: {result.get('error')}")
        print("=" * 80)
    else:
        print("   No tools were used - AI didn't attempt booking")

    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_booking_with_zoom())
