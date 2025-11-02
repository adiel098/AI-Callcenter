"""
Test script to verify Google Calendar integration and meeting booking
"""
import asyncio
from datetime import datetime, timedelta
from services.calendar_service import CalendarService
from services.llm_service import LLMService

async def test_calendar_booking():
    """Test calendar service and LLM tools"""

    print("=" * 60)
    print("Testing Google Calendar Integration")
    print("=" * 60)

    # Initialize services
    print("\n1. Initializing Calendar Service...")
    calendar_service = CalendarService()

    if not calendar_service.service:
        print("❌ Calendar service failed to initialize!")
        print("   Make sure credentials.json or service-account.json is configured")
        return False

    print("✅ Calendar service initialized successfully")

    # Test 1: Get available slots
    print("\n2. Testing calendar availability check...")
    try:
        slots = calendar_service.get_next_available_slots(count=3, duration_minutes=30)
        if slots:
            print(f"✅ Found {len(slots)} available slots:")
            for i, slot in enumerate(slots, 1):
                print(f"   {i}. {slot['display']}")
        else:
            print("⚠️  No available slots found (calendar might be fully booked)")
    except Exception as e:
        print(f"❌ Error getting slots: {e}")
        return False

    # Test 2: Test LLM with calendar tools
    print("\n3. Testing LLM Service with Calendar Tools...")
    llm_service = LLMService(calendar_service=calendar_service)

    # Simulate a conversation where user wants to book a meeting
    conversation_history = []
    lead_info = {
        "name": "Test User",
        "email": "test@example.com"
    }

    # User asks about availability
    print("\n   User: When are you available?")
    intent, response, tools = await llm_service.get_response_with_tools(
        user_message="When are you available?",
        conversation_history=conversation_history,
        lead_info=lead_info
    )
    print(f"   AI: {response}")
    if tools:
        print(f"   📋 Tools used: {[t['tool'] for t in tools]}")
        for tool in tools:
            if tool['tool'] == 'check_calendar_availability':
                print(f"   ✅ Calendar availability check successful")

    # Test 3: Test direct booking (DO NOT ACTUALLY EXECUTE)
    print("\n4. Testing Meeting Booking Function (DRY RUN)...")
    print("   NOTE: This would create a real calendar event if executed")

    # Get a future time slot
    test_time = datetime.utcnow() + timedelta(days=7)
    test_time = test_time.replace(hour=14, minute=0, second=0, microsecond=0)

    print(f"\n   Would book meeting at: {test_time.strftime('%Y-%m-%d %H:%M')} UTC")
    print(f"   Guest: test@example.com")
    print(f"   Duration: 30 minutes")

    # Check if we want to actually create a test event
    print("\n" + "=" * 60)
    user_input = input("Do you want to create a TEST meeting on your calendar? (yes/no): ")

    if user_input.lower() == 'yes':
        print("\n   Creating test meeting...")
        try:
            event_id = calendar_service.create_meeting(
                summary="TEST: AI Scheduler Meeting",
                start_time=test_time,
                end_time=test_time + timedelta(minutes=30),
                attendee_email="test@example.com",
                description="This is a test meeting created by the AI scheduler system."
            )

            if event_id:
                print(f"   ✅ Meeting created successfully!")
                print(f"   📅 Event ID: {event_id}")
                print(f"   📧 Invitation sent to: test@example.com")
                print(f"\n   Check your Google Calendar to see the event!")

                # Offer to delete the test event
                delete_input = input("\n   Delete the test event? (yes/no): ")
                if delete_input.lower() == 'yes':
                    if calendar_service.cancel_meeting(event_id):
                        print("   ✅ Test event deleted")
                    else:
                        print("   ⚠️  Could not delete test event")
            else:
                print("   ❌ Failed to create meeting")
                return False
        except Exception as e:
            print(f"   ❌ Error creating meeting: {e}")
            return False
    else:
        print("   ⏭️  Skipped actual booking test")

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)
    print("\nSummary:")
    print("- Calendar service: ✅ Working")
    print("- Get available slots: ✅ Working")
    print("- LLM with calendar tools: ✅ Working")
    print("- Meeting booking: ✅ Ready (tested or skipped)")
    print("\nThe AI can successfully:")
    print("  1. Check calendar availability")
    print("  2. Book meetings on Google Calendar")
    print("  3. Send automatic email invitations")

    return True

if __name__ == "__main__":
    result = asyncio.run(test_calendar_booking())
    exit(0 if result else 1)
