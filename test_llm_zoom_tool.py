"""
Test LLM service with Zoom tool integration
"""
import asyncio
from datetime import datetime, timedelta
from backend.services.llm_service import LLMService
from backend.services.calendar_service import CalendarService
from backend.services.zoom_service import ZoomService

async def test_llm_zoom_tool():
    """Test LLM can book meetings with Zoom links"""
    print("=" * 60)
    print("Testing LLM Service with Zoom Tool Integration")
    print("=" * 60)

    # Initialize services
    calendar_service = CalendarService()
    zoom_service = ZoomService()
    llm_service = LLMService(
        calendar_service=calendar_service,
        zoom_service=zoom_service
    )

    # Lead information
    lead_info = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567890",
        "company": "TechCorp"
    }

    # Simulate conversation history
    conversation_history = [
        {"role": "assistant", "content": "Hi Jane! I'm calling from Alta AI. We help businesses automate their revenue operations. Do you have a few minutes to chat?"},
        {"role": "user", "content": "Yes, I'm interested. When can we meet?"},
        {"role": "assistant", "content": "Great! Let me check my calendar availability."}
    ]

    print("\nLead Information:")
    print(f"  Name: {lead_info['name']}")
    print(f"  Email: {lead_info['email']}")
    print(f"  Company: {lead_info['company']}")

    # Test 1: Check calendar availability
    print("\n" + "=" * 60)
    print("Test 1: AI checks calendar availability")
    print("=" * 60)

    user_message = "What times do you have available next week?"
    print(f"\nUser says: \"{user_message}\"")

    intent, response, tool_calls = await llm_service.get_response_with_tools(
        user_message=user_message,
        conversation_history=conversation_history,
        lead_info=lead_info
    )

    print(f"\nAI Intent: {intent}")
    print(f"AI Response: {response}")
    print(f"Tools Used: {len(tool_calls)} tool(s)")

    if tool_calls:
        for i, tool in enumerate(tool_calls, 1):
            print(f"\n  Tool {i}:")
            print(f"    Name: {tool.get('tool_name', tool.get('name', 'Unknown'))}")
            print(f"    Arguments: {tool.get('arguments', tool.get('args', {}))}")
            result = tool.get('result', tool.get('output', 'N/A'))
            if isinstance(result, dict):
                print(f"    Result Success: {result.get('success', 'N/A')}")
                print(f"    Result Data: {result}")
            else:
                print(f"    Result: {result}")

    # Update conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": response})

    # Test 2: Book meeting with Zoom
    print("\n" + "=" * 60)
    print("Test 2: AI books meeting with Zoom link")
    print("=" * 60)

    # Calculate a specific time next week
    next_week = datetime.utcnow() + timedelta(days=7)
    meeting_time = next_week.replace(hour=14, minute=0, second=0, microsecond=0)
    meeting_time_str = meeting_time.strftime("%Y-%m-%d at 2:00 PM")

    user_message = f"Perfect! Let's book {meeting_time_str} UTC. My email is {lead_info['email']}"
    print(f"\nUser says: \"{user_message}\"")

    intent, response, tool_calls = await llm_service.get_response_with_tools(
        user_message=user_message,
        conversation_history=conversation_history,
        lead_info=lead_info
    )

    print(f"\nAI Intent: {intent}")
    print(f"AI Response: {response}")
    print(f"Tools Used: {len(tool_calls)} tool(s)")

    zoom_created = False
    calendar_created = False
    zoom_url = None
    event_id = None

    if tool_calls:
        for i, tool in enumerate(tool_calls, 1):
            print(f"\n  Tool {i}: {tool}")
            tool_name = tool.get('tool_name', tool.get('name', 'Unknown'))
            print(f"    Name: {tool_name}")
            print(f"    Arguments: {tool.get('arguments', tool.get('args', {}))}")

            # Try multiple possible result keys
            result = tool.get('result', tool.get('output', tool.get('return_value', {})))

            if tool_name == 'book_meeting' or 'book_meeting' in str(tool):
                print(f"    Result: {result}")
                if isinstance(result, dict) and result.get('success'):
                    calendar_created = True
                    event_id = result.get('event_id')
                    zoom_url = result.get('zoom_link')

                    print(f"    Event ID: {event_id}")
                    print(f"    Zoom Link: {zoom_url}")
                    print(f"    Meeting Link: {result.get('google_meet_link', 'None')}")

                    if zoom_url:
                        zoom_created = True

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if calendar_created and zoom_created:
        print("[SUCCESS] LLM successfully booked meeting with Zoom link!")
        print(f"\n  Calendar Event ID: {event_id}")
        print(f"  Zoom Join URL: {zoom_url}")
        print(f"\n  The AI was able to:")
        print("    - Check calendar availability")
        print("    - Create Zoom meeting")
        print("    - Book calendar event")
        print("    - Include Zoom link in booking")
        print("\n  Integration Status: FULLY WORKING")
    elif calendar_created:
        print("[PARTIAL] LLM booked meeting but no Zoom link")
        print(f"\n  Calendar Event ID: {event_id}")
        print("\n  Possible reasons:")
        print("    - Zoom credentials not configured")
        print("    - Zoom service not injected into LLM")
        print("    - Check ZOOM_SETUP.md for setup instructions")
    else:
        print("[FAILED] LLM could not book meeting")
        print("\n  Check:")
        print("    - Calendar service configuration")
        print("    - LLM tool definitions")
        print("    - Error logs above")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_llm_zoom_tool())
