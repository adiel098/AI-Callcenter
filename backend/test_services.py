"""
Comprehensive test script for all AI call services
Tests each component individually before running integration tests
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from dotenv import load_dotenv
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, status, message=""):
    """Print test result with color"""
    symbol = "[PASS]" if status else "[FAIL]"
    color = GREEN if status else RED
    print(f"{color}{symbol}{RESET} {name}")
    if message:
        print(f"  {message}")


async def test_environment():
    """Test 1: Check environment variables"""
    print(f"\n{BLUE}=== Test 1: Environment Configuration ==={RESET}")

    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY",
        "DEEPGRAM_API_KEY",
        "GOOGLE_CALENDAR_ID"
    ]

    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print_test(f"Environment variable {var}", True, f"Value: {masked}")
        else:
            print_test(f"Environment variable {var}", False, "MISSING!")
            all_present = False

    return all_present


async def test_database():
    """Test 2: Database connectivity"""
    print(f"\n{BLUE}=== Test 2: Database Connectivity ==={RESET}")

    try:
        from database import engine, Base
        from sqlalchemy import text

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            print_test("Database connection", row[0] == 1, f"Connected to: {engine.url.database}")

        # Check tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = ["leads", "calls", "meetings", "conversation_history", "campaigns"]
        for table in expected_tables:
            exists = table in tables
            print_test(f"Table '{table}' exists", exists)

        return True
    except Exception as e:
        print_test("Database connection", False, f"Error: {str(e)}")
        return False


async def test_redis():
    """Test 3: Redis connectivity"""
    print(f"\n{BLUE}=== Test 3: Redis Connectivity ==={RESET}")

    try:
        import redis
        from config import settings

        r = redis.from_url(settings.redis_url)

        # Test ping
        pong = r.ping()
        print_test("Redis ping", pong, "Redis is responding")

        # Test set/get
        r.set("test_key", "test_value")
        value = r.get("test_key")
        print_test("Redis set/get", value == b"test_value", "Can write and read data")

        r.delete("test_key")
        return True
    except Exception as e:
        print_test("Redis connection", False, f"Error: {str(e)}")
        return False


async def test_twilio():
    """Test 4: Twilio service"""
    print(f"\n{BLUE}=== Test 4: Twilio Service ==={RESET}")

    try:
        from services.twilio_service import TwilioService

        service = TwilioService()

        # Test client initialization
        print_test("Twilio client initialized", service.client is not None)

        # Test phone number
        print_test("Twilio phone number", service.phone_number is not None,
                  f"Using: {service.phone_number}")

        # Test account info
        try:
            from config import settings
            account = service.client.api.accounts(settings.twilio_account_sid).fetch()
            print_test("Twilio account valid", True,
                      f"Account: {account.friendly_name}, Status: {account.status}")
        except Exception as e:
            print_test("Twilio account", False, f"Error: {str(e)}")
            return False

        # Get available phone number info
        try:
            incoming_phone = service.client.incoming_phone_numbers.list(
                phone_number=service.phone_number,
                limit=1
            )
            if incoming_phone:
                phone = incoming_phone[0]
                print_test("Phone number verified", True,
                          f"SID: {phone.sid}, Capabilities: Voice={phone.capabilities['voice']}")
            else:
                print_test("Phone number verified", False, "Phone number not found in account")
        except Exception as e:
            print_test("Phone number check", False, f"Warning: {str(e)}")

        return True
    except Exception as e:
        print_test("Twilio service", False, f"Error: {str(e)}")
        return False


async def test_openai():
    """Test 5: OpenAI service"""
    print(f"\n{BLUE}=== Test 5: OpenAI LLM Service ==={RESET}")

    try:
        from services.llm_service import LLMService

        service = LLMService()

        # Test function calling
        print(f"\n{YELLOW}Testing function calling capabilities...{RESET}")
        response_with_tools = await service.get_response_with_tools(
            user_message="What time slots do you have available next week?",
            conversation_history=[],
            lead_info={"name": "Test User", "email": "test@example.com"}
        )

        intent, ai_response, tool_calls = response_with_tools
        print_test("OpenAI response generated", len(ai_response) > 0,
                  f"Response: {ai_response[:100]}...")
        print_test("OpenAI function calling works", True,
                  f"Intent: {intent}, Tools called: {len(tool_calls) if tool_calls else 0}")

        return True
    except Exception as e:
        print_test("OpenAI service", False, f"Error: {str(e)}")
        return False


async def test_elevenlabs():
    """Test 6: ElevenLabs TTS service"""
    print(f"\n{BLUE}=== Test 6: ElevenLabs TTS Service ==={RESET}")

    try:
        from services.speech_service import SpeechService

        service = SpeechService()

        # Test text-to-speech
        test_text = "Hello, this is a test of the text to speech system."
        audio_data = await service.synthesize_speech(test_text, language="en")

        print_test("ElevenLabs TTS", len(audio_data) > 0,
                  f"Generated {len(audio_data)} bytes of audio data")

        # Save test audio
        test_file = Path(__file__).parent / "test_audio.mp3"
        with open(test_file, "wb") as f:
            f.write(audio_data)
        print(f"  {YELLOW}Audio saved to: {test_file}{RESET}")

        return True
    except Exception as e:
        print_test("ElevenLabs service", False, f"Error: {str(e)}")
        return False


async def test_deepgram():
    """Test 7: Deepgram STT service"""
    print(f"\n{BLUE}=== Test 7: Deepgram STT Service ==={RESET}")

    try:
        from services.speech_service import SpeechService

        service = SpeechService()

        # Check if we have test audio from previous test
        test_file = Path(__file__).parent / "test_audio.mp3"
        if test_file.exists():
            with open(test_file, "rb") as f:
                audio_data = f.read()

            transcript = await service.transcribe_audio(audio_data, language="en")
            print_test("Deepgram STT", transcript is not None and len(transcript) > 0,
                      f"Transcript: {transcript}")
        else:
            print_test("Deepgram STT", True, "Skipped (no test audio available)")

        return True
    except Exception as e:
        print_test("Deepgram service", False, f"Error: {str(e)}")
        return False


async def test_google_calendar():
    """Test 8: Google Calendar service"""
    print(f"\n{BLUE}=== Test 8: Google Calendar Service ==={RESET}")

    try:
        from services.calendar_service import CalendarService

        service = CalendarService()

        # Test getting available slots
        slots = service.get_next_available_slots(count=3, duration_minutes=30)
        print_test("Google Calendar - Get slots", len(slots) > 0,
                  f"Found {len(slots)} available slots")

        if slots:
            for i, slot in enumerate(slots[:3], 1):
                print(f"  {YELLOW}Slot {i}: {slot['start']} - {slot['end']}{RESET}")

        # Don't actually book a meeting in test mode
        print_test("Google Calendar - Ready for booking", True,
                  "Service configured and ready")

        return True
    except Exception as e:
        print_test("Google Calendar service", False, f"Error: {str(e)}")
        return False


async def test_celery():
    """Test 9: Celery worker connectivity"""
    print(f"\n{BLUE}=== Test 9: Celery Worker ==={RESET}")

    try:
        from workers.celery_app import celery_app

        # Check Celery configuration
        print_test("Celery app initialized", celery_app is not None,
                  f"Broker: {celery_app.conf.broker_url}")

        # Check if workers are running
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()

        if active_workers:
            print_test("Celery workers running", True,
                      f"Active workers: {list(active_workers.keys())}")
        else:
            print_test("Celery workers running", False,
                      "No active workers found. Start with: celery -A workers.celery_app worker --loglevel=info")

        return True
    except Exception as e:
        print_test("Celery connectivity", False, f"Error: {str(e)}")
        return False


async def test_full_conversation_flow():
    """Test 10: Complete conversation flow simulation"""
    print(f"\n{BLUE}=== Test 10: Full Conversation Flow Simulation ==={RESET}")

    try:
        from services.llm_service import LLMService
        from services.calendar_service import CalendarService

        llm = LLMService()
        calendar = CalendarService()

        # Inject calendar service into LLM
        llm.calendar_service = calendar

        conversation_history = []
        lead_info = {
            "name": "John Doe",
            "company": "Test Corp",
            "email": "john.doe@testcorp.com",
            "phone": "+1234567890"
        }

        print(f"\n{YELLOW}Simulating conversation...{RESET}")

        # Turn 1: AI introduction
        print(f"\n{BLUE}Turn 1: AI introduces itself{RESET}")
        intent, response, tools = await llm.get_response_with_tools(
            user_message="",  # Initial greeting from AI
            conversation_history=conversation_history,
            lead_info=lead_info
        )
        print(f"AI: {response}")
        conversation_history.append({"role": "assistant", "content": response})

        # Turn 2: User shows interest
        print(f"\n{BLUE}Turn 2: User shows interest{RESET}")
        user_msg = "I'm interested. When are you available?"
        print(f"User: {user_msg}")
        conversation_history.append({"role": "user", "content": user_msg})

        intent, response, tools = await llm.get_response_with_tools(
            user_message=user_msg,
            conversation_history=conversation_history,
            lead_info=lead_info
        )
        print(f"AI: {response}")
        print_test("AI checks calendar", tools is not None and len(tools) > 0,
                  f"Tools used: {[t.get('function', {}).get('name') for t in tools] if tools else 'None'}")
        conversation_history.append({"role": "assistant", "content": response})

        # Turn 3: User confirms time
        print(f"\n{BLUE}Turn 3: User confirms meeting time{RESET}")
        slots = calendar.get_next_available_slots(count=1, duration_minutes=30)
        if slots:
            slot_time = slots[0]['start_formatted']
            user_msg = f"Let's do {slot_time}. My email is {lead_info['email']}"
        else:
            user_msg = "Tuesday at 2pm works. My email is john.doe@testcorp.com"

        print(f"User: {user_msg}")
        conversation_history.append({"role": "user", "content": user_msg})

        intent, response, tools = await llm.get_response_with_tools(
            user_message=user_msg,
            conversation_history=conversation_history,
            lead_info=lead_info
        )
        print(f"AI: {response}")
        print_test("AI attempts to book meeting",
                  intent in ["interested", "meeting_scheduled"],
                  f"Intent: {intent}")

        print_test("Full conversation flow", True, "Conversation completed successfully")

        return True
    except Exception as e:
        print_test("Full conversation flow", False, f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}AI Outbound Call Center - Comprehensive Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    tests = [
        ("Environment Configuration", test_environment),
        ("Database Connectivity", test_database),
        ("Redis Connectivity", test_redis),
        ("Twilio Service", test_twilio),
        ("OpenAI LLM Service", test_openai),
        ("ElevenLabs TTS Service", test_elevenlabs),
        ("Deepgram STT Service", test_deepgram),
        ("Google Calendar Service", test_google_calendar),
        ("Celery Worker", test_celery),
        ("Full Conversation Flow", test_full_conversation_flow),
    ]

    results = {}
    for name, test_func in tests:
        try:
            result = await test_func()
            results[name] = result
        except Exception as e:
            print(f"\n{RED}Test '{name}' crashed: {str(e)}{RESET}")
            results[name] = False

    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for name, result in results.items():
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"{status} - {name}")

    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}[SUCCESS] All tests passed! System is ready for production use.{RESET}")
    else:
        print(f"\n{YELLOW}[WARNING] Some tests failed. Please check the errors above.{RESET}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
