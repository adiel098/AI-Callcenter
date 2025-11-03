"""
LLM Service with OpenAI Function Calling (Tools)
Enables the AI to check calendars, book meetings, and send emails during calls.
"""
from openai import AsyncOpenAI
import logging
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import SessionLocal
from backend.models.setting import Setting
from backend.services.cache_service import get_cache_service

logger = logging.getLogger(__name__)
settings = get_settings()


class ConversationIntent:
    """Intent classifications for call outcomes"""
    INTERESTED = "INTERESTED"
    NOT_INTERESTED = "NOT_INTERESTED"
    NEEDS_INFO = "NEEDS_INFO"
    SCHEDULE_MEETING = "SCHEDULE_MEETING"
    MEETING_BOOKED = "MEETING_BOOKED"
    END_CALL = "END_CALL"


class LLMService:
    """
    LLM service with function calling capabilities.

    The AI can execute real actions during calls:
    - Check calendar availability
    - Book meetings (Google Calendar handles email invitations automatically)
    """

    def __init__(self, calendar_service=None, zoom_service=None):
        """
        Initialize LLM service with tool support

        Args:
            calendar_service: CalendarService instance for booking
            zoom_service: ZoomService instance for video links (optional)
        """
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"  # Fast and cost-effective
        self.recently_offered_slots = []  # Track slots from check_calendar_availability
        self.system_prompt = self._load_system_prompt()

        # Services for executing tools
        self.calendar_service = calendar_service
        self.zoom_service = zoom_service

    def _load_system_prompt(self) -> str:
        """
        Load the base system prompt from database (with cache) or file fallback.

        Priority:
        1. Redis cache (5-min TTL)
        2. Database settings table
        3. File (prompts/system_prompt_en.txt)
        4. Hardcoded fallback

        Returns:
            System prompt string
        """
        cache_key = "settings:system_prompt_en"
        cache = get_cache_service()

        # Try cache first
        cached_prompt = cache.get(cache_key)
        if cached_prompt:
            logger.debug("System prompt loaded from cache")
            return cached_prompt

        # Try database
        try:
            db = SessionLocal()
            setting = db.query(Setting).filter(Setting.key == "system_prompt_en").first()
            db.close()

            if setting and setting.value:
                logger.info("System prompt loaded from database")
                # Cache for 5 minutes
                cache.set(cache_key, setting.value, ttl=300)
                return setting.value
        except Exception as e:
            logger.warning(f"Failed to load system prompt from database: {e}")

        # Try file fallback
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_path = prompts_dir / "system_prompt_en.txt"

        if prompt_path.exists():
            file_prompt = prompt_path.read_text(encoding="utf-8")
            logger.info("System prompt loaded from file (fallback)")
            cache.set(cache_key, file_prompt, ttl=300)
            return file_prompt

        # Final fallback
        logger.warning("Using hardcoded system prompt (all sources failed)")
        return "You are a professional AI assistant scheduling meetings."

    async def generate_opening_message(self, lead_info: Dict[str, Any]) -> str:
        """
        Generate personalized opening message for a lead.

        This replaces the generic greeting with an AI-generated personal message
        that follows the system prompt's example opening and mentions the lead's name.

        Args:
            lead_info: Dictionary with 'name', 'email', optionally 'company'

        Returns:
            Personalized opening message (1-2 sentences)
        """
        try:
            lead_name = lead_info.get('name', 'there')

            # Use the system prompt's example opening as a template
            opening_template = f"""Hi {lead_name}, this is Alex calling from Alta AI. How are you doing today?"""

            logger.info(f"Generated opening for {lead_name}")
            return opening_template

        except Exception as e:
            logger.error(f"Failed to generate opening message: {e}")
            # Fallback to simple greeting
            return f"Hi {lead_info.get('name', 'there')}, this is Alex from Alta AI. How are you doing today?"

    def _get_system_prompt_with_tools(self) -> str:
        """Get system prompt enhanced with tool instructions"""
        base_prompt = self.system_prompt

        tool_instructions = """

IMPORTANT: You have access to these tools for real actions:

1. check_calendar_availability - Check available meeting time slots
2. book_meeting - Book a meeting on the calendar (automatically sends Google Calendar invitation to guest email)

Use these tools when appropriate:
- When user asks "When are you available?", use check_calendar_availability
- When user agrees to a time, use book_meeting immediately

🚨 CRITICAL EMAIL HANDLING:
- Check the CONVERSATION CONTEXT for the lead's email address
- If email is already provided in context, use it directly for booking WITHOUT asking again
- Only ask for email if it's NOT available in the conversation context
- When user says "you already have it", they're referring to the email in context - use it immediately

⚠️ TOOL EXECUTION REQUIREMENT:
- You MUST actually CALL the book_meeting tool - saying "I'll book it" is NOT enough
- Only use past tense ("I've booked") AFTER successfully calling the tool
- Never use future tense ("I'll book") as a substitute for calling the tool

Google Calendar will automatically send the invitation and reminders when book_meeting is called.
"""
        return base_prompt + tool_instructions

    def _get_tools_definition(self) -> List[Dict]:
        """
        Define available tools for OpenAI function calling

        Returns:
            List of tool definitions in OpenAI format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "check_calendar_availability",
                    "description": "Check available meeting slots in the calendar. Use this when user asks about availability.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "preferred_date": {
                                "type": "string",
                                "description": "Preferred date (e.g., 'tomorrow', 'next Tuesday', '2025-01-10')"
                            },
                            "duration_minutes": {
                                "type": "number",
                                "description": "Meeting duration in minutes",
                                "default": 30
                            },
                            "num_slots": {
                                "type": "number",
                                "description": "Number of alternative slots to return",
                                "default": 3
                            }
                        },
                        "required": ["preferred_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "book_meeting",
                    "description": "Book a meeting on the calendar. ONLY use after user confirms time and provides email.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "datetime": {
                                "type": "string",
                                "description": "Meeting datetime in ISO format (e.g., '2025-01-10T14:00:00')"
                            },
                            "duration_minutes": {
                                "type": "number",
                                "description": "Meeting duration in minutes",
                                "default": 30
                            },
                            "guest_email": {
                                "type": "string",
                                "description": "Guest's email address"
                            },
                            "guest_name": {
                                "type": "string",
                                "description": "Guest's full name"
                            },
                            "meeting_title": {
                                "type": "string",
                                "description": "Meeting title/subject",
                                "default": "Sales Meeting"
                            },
                            "description": {
                                "type": "string",
                                "description": "Meeting agenda or description (optional)"
                            }
                        },
                        "required": ["datetime", "guest_email", "guest_name"]
                    }
                }
            }
        ]

    async def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool function

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool

        Returns:
            Tool execution result
        """
        try:
            logger.info("=" * 80)
            logger.info(f"🔧 TOOL EXECUTION: {tool_name}")
            logger.info(f"Arguments: {json.dumps(tool_args, indent=2, default=str)}")
            logger.info("=" * 80)

            result = None

            if tool_name == "check_calendar_availability":
                logger.info("📅 Executing: check_calendar_availability")
                result = await self._check_calendar_availability(tool_args)

            elif tool_name == "book_meeting":
                logger.info("📆 Executing: book_meeting")
                result = await self._book_meeting(tool_args)

            else:
                logger.error(f"❌ Unknown tool requested: {tool_name}")
                return {"error": f"Unknown tool: {tool_name}"}

            logger.info("=" * 80)
            logger.info(f"✅ TOOL RESULT: {tool_name}")
            logger.info(f"Result: {json.dumps(result, indent=2, default=str)}")
            logger.info("=" * 80)

            return result

        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ TOOL EXECUTION ERROR: {tool_name}")
            logger.error(f"   - Error: {str(e)}")
            logger.error(f"   - Type: {type(e).__name__}")
            logger.error(f"   - Full traceback:", exc_info=True)
            logger.error("=" * 80)
            return {"error": str(e)}

    def _parse_date_string(self, date_str: str) -> datetime:
        """
        Parse natural language or ISO date string to datetime.

        Supports:
        - Natural language: "tomorrow", "next week", "next Monday", "in 3 days"
        - ISO format: "2025-01-10"
        - Relative: "in X days"

        Args:
            date_str: Date string to parse

        Returns:
            Parsed datetime object (defaults to tomorrow if unparseable)
        """
        date_str_lower = date_str.lower().strip()
        now = datetime.utcnow()

        # Handle common natural language dates
        if date_str_lower == "tomorrow":
            return now + timedelta(days=1)
        elif date_str_lower == "next week":
            return now + timedelta(days=7)
        elif "next" in date_str_lower:
            # For "next Monday", "next Tuesday", etc., default to next week
            return now + timedelta(days=7)
        elif "in" in date_str_lower and "day" in date_str_lower:
            # Handle "in 3 days", "in 5 days", etc.
            try:
                days = int(''.join(filter(str.isdigit, date_str_lower)))
                return now + timedelta(days=days)
            except ValueError:
                return now + timedelta(days=1)
        else:
            # Try parsing as ISO format (e.g., "2025-01-10")
            try:
                return datetime.fromisoformat(date_str)
            except (ValueError, TypeError):
                # Default to tomorrow if unparseable
                logger.warning(f"Could not parse date '{date_str}', defaulting to tomorrow")
                return now + timedelta(days=1)

    async def _check_calendar_availability(self, args: Dict) -> Dict:
        """
        Check calendar availability and return free slots.

        Args:
            args: Dictionary containing:
                - preferred_date: Natural language date (e.g., "next week", "tomorrow")
                - duration_minutes: Meeting duration (default: 30)
                - num_slots: Number of slots to return (default: 3)

        Returns:
            Dictionary with success status and available slots
        """
        logger.info("📅 CHECK CALENDAR AVAILABILITY - Starting")
        logger.info(f"Request args: {json.dumps(args, indent=2)}")

        if not self.calendar_service:
            logger.error("❌ Calendar service not available")
            return {
                "success": False,
                "error": "Calendar service is not configured. Please contact support."
            }

        try:
            duration = args.get("duration_minutes", 30)
            num_slots = args.get("num_slots", 3)
            preferred_date = args.get("preferred_date", "tomorrow")

            logger.info(f"   - Preferred date (input): {preferred_date}")
            logger.info(f"   - Duration: {duration} minutes")
            logger.info(f"   - Number of slots requested: {num_slots}")

            # Parse the preferred date
            start_date = self._parse_date_string(preferred_date)
            logger.info(f"✅ Date parsed successfully")
            logger.info(f"   - Start date: {start_date.strftime('%A, %B %d, %Y at %I:%M %p')}")

            # Calculate end date (2 weeks from preferred date)
            end_date = start_date + timedelta(days=14)
            logger.info(f"   - End date: {end_date.strftime('%A, %B %d, %Y')}")

            # Get available slots from calendar service
            logger.info("🔍 Querying calendar for available slots...")
            slots = self.calendar_service.get_available_slots(
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration
            )

            logger.info(f"✅ Calendar query complete - found {len(slots)} total slots")

            # Store the actual slot objects for validation during booking
            selected_slots = slots[:num_slots]
            self.recently_offered_slots = selected_slots

            # Extract just the display strings for the LLM
            display_slots = [slot['display'] for slot in selected_slots]

            logger.info(f"📋 Returning {len(display_slots)} slots to AI:")
            for i, slot in enumerate(display_slots, 1):
                logger.info(f"   {i}. {slot}")
                logger.info(f"      Stored datetime: {selected_slots[i-1]['start']}")

            return {
                "success": True,
                "available_slots": display_slots
            }

        except Exception as e:
            logger.error(f"❌ Error checking calendar availability: {e}")
            logger.error(f"   - Error type: {type(e).__name__}")
            logger.error(f"   - Full traceback:", exc_info=True)
            return {"success": False, "error": str(e)}

    async def _book_meeting(self, args: Dict) -> Dict:
        """
        Book a meeting on Google Calendar with Zoom video conferencing.

        This method:
        1. Creates a Zoom meeting (if ZoomService is configured)
        2. Creates a Google Calendar event with Zoom link in description
        3. Google Calendar automatically sends invite email to the attendee

        Args:
            args: Dictionary containing:
                - datetime: ISO format datetime string (required)
                - guest_email: Guest's email address (required)
                - guest_name: Guest's name (required)
                - duration_minutes: Meeting duration (default: 30)
                - meeting_title: Meeting title (default: "Sales Meeting")
                - description: Meeting description (optional)

        Returns:
            Dictionary with success status, event_id, zoom_link, and video_link
            Example: {
                "success": True,
                "event_id": "abc123",
                "zoom_link": "https://zoom.us/j/123456789",
                "video_link": "https://zoom.us/j/123456789",
                "message": "Meeting booked with Zoom link..."
            }
        """
        logger.info("=" * 80)
        logger.info("BOOKING MEETING - Starting process")
        logger.info("=" * 80)
        logger.info(f"Booking args received: {json.dumps(args, indent=2)}")

        if not self.calendar_service:
            logger.error("❌ Calendar service not available for booking")
            return {
                "success": False,
                "error": "Calendar service is not configured. Please contact support."
            }

        try:
            # Validate and parse datetime
            logger.info(f"📅 Parsing datetime: {args.get('datetime')}")
            try:
                meeting_datetime = datetime.fromisoformat(args["datetime"])
                logger.info(f"✅ DateTime parsed successfully: {meeting_datetime}")
                logger.info(f"   - Date: {meeting_datetime.strftime('%A, %B %d, %Y')}")
                logger.info(f"   - Time: {meeting_datetime.strftime('%I:%M %p')} UTC")
            except (ValueError, KeyError) as e:
                logger.error(f"❌ Invalid datetime format: {args.get('datetime')} - Error: {e}")
                return {
                    "success": False,
                    "error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                }

            # Validate that the datetime matches one of the recently offered slots
            if self.recently_offered_slots:
                logger.info("🔍 Validating datetime against recently offered slots...")
                offered_datetimes = [slot['start'] for slot in self.recently_offered_slots]

                # Compare date and time (ignore timezone/microseconds)
                matching_slot = None
                for offered_dt in offered_datetimes:
                    if (meeting_datetime.date() == offered_dt.date() and
                        meeting_datetime.hour == offered_dt.hour and
                        meeting_datetime.minute == offered_dt.minute):
                        matching_slot = offered_dt
                        break

                if matching_slot:
                    logger.info(f"✅ Datetime matches offered slot: {matching_slot.strftime('%A, %B %d at %I:%M %p')}")
                else:
                    logger.warning(f"⚠️ WARNING: Datetime does NOT match any offered slots!")
                    logger.warning(f"   - Requested: {meeting_datetime.strftime('%A, %B %d at %I:%M %p')}")
                    logger.warning(f"   - Offered slots were:")
                    for i, slot in enumerate(self.recently_offered_slots, 1):
                        logger.warning(f"      {i}. {slot['display']} ({slot['start'].strftime('%Y-%m-%d %H:%M')})")
                    logger.warning("   - Proceeding with booking anyway, but AI may have selected wrong date!")
            else:
                logger.info("ℹ️ No recently offered slots to validate against (first booking or cache cleared)")

            duration = args.get("duration_minutes", 30)
            end_time = meeting_datetime + timedelta(minutes=duration)
            meeting_title = args.get("meeting_title", "Sales Meeting")
            meeting_description = args.get("description", f"Meeting with {args['guest_name']}")

            logger.info(f"📋 Meeting details:")
            logger.info(f"   - Title: {meeting_title}")
            logger.info(f"   - Guest Name: {args.get('guest_name')}")
            logger.info(f"   - Guest Email: {args.get('guest_email')}")
            logger.info(f"   - Duration: {duration} minutes")
            logger.info(f"   - Start: {meeting_datetime.isoformat()}")
            logger.info(f"   - End: {end_time.isoformat()}")

            # Create Zoom meeting if service is available
            zoom_link = None
            if self.zoom_service:
                logger.info("🎥 Zoom service available - attempting to create Zoom meeting")
                try:
                    zoom_meeting = self.zoom_service.create_meeting(
                        topic=meeting_title,
                        start_time=meeting_datetime,
                        duration=duration,
                        agenda=meeting_description
                    )
                    if zoom_meeting:
                        zoom_link = zoom_meeting['join_url']
                        logger.info(f"✅ Zoom meeting created successfully")
                        logger.info(f"   - Join URL: {zoom_link}")
                        logger.info(f"   - Meeting ID: {zoom_meeting['meeting_id']}")
                        logger.info(f"   - Password: {zoom_meeting.get('password', 'N/A')}")

                        # Add Zoom link to calendar description
                        meeting_description += f"\n\nJoin Zoom Meeting:\n{zoom_meeting['join_url']}\n"
                        meeting_description += f"Meeting ID: {zoom_meeting['meeting_id']}\n"
                        meeting_description += f"Password: {zoom_meeting['password']}"
                    else:
                        logger.warning("⚠️ Zoom service returned None - no meeting created")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create Zoom meeting (continuing without): {e}")
            else:
                logger.info("ℹ️ No Zoom service available - skipping Zoom meeting creation")

            # Create meeting via calendar service
            logger.info("📆 Creating Google Calendar event...")
            logger.info(f"   - Summary: {meeting_title}")
            logger.info(f"   - Attendee: {args['guest_email']}")
            logger.info(f"   - Description length: {len(meeting_description)} chars")

            result = self.calendar_service.create_meeting(
                summary=meeting_title,
                start_time=meeting_datetime,
                end_time=end_time,
                attendee_email=args["guest_email"],
                description=meeting_description
            )

            if not result:
                logger.error("❌ Calendar service returned None - failed to create event")
                return {"success": False, "error": "Failed to create calendar event"}

            event_id = result['event_id']

            logger.info("✅ MEETING BOOKED SUCCESSFULLY!")
            logger.info(f"   - Event ID: {event_id}")
            logger.info(f"   - Zoom Link: {zoom_link or 'N/A'}")
            logger.info(f"   - Calendar invite automatically sent to: {args['guest_email']}")
            logger.info("=" * 80)

            # Determine final video link (Zoom only)
            video_link = zoom_link

            return {
                "success": True,
                "event_id": event_id,
                "zoom_link": zoom_link,
                "video_link": video_link,  # Generic field for video conferencing
                "message": f"Meeting booked{' with Zoom link' if zoom_link else ''} and calendar invite sent to {args['guest_email']}"
            }

        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ MEETING BOOKING ERROR: {e}")
            logger.error(f"   - Error type: {type(e).__name__}")
            logger.error(f"   - Full traceback:", exc_info=True)
            logger.error("=" * 80)
            return {"success": False, "error": str(e)}

    async def get_response_with_tools(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        lead_info: Optional[Dict] = None
    ) -> Tuple[str, str, Optional[List[Dict]]]:
        """
        Get AI response with tool calling support

        Args:
            user_message: User's spoken message
            conversation_history: Previous conversation turns
            lead_info: Lead information (name, email)

        Returns:
            Tuple of (intent, response_text, tool_calls)
        """
        try:
            # Build messages for API
            messages = [
                {"role": "system", "content": self._get_system_prompt_with_tools()}
            ]

            # Add lead context if available
            if lead_info:
                lead_name = lead_info.get('name', 'Unknown')
                lead_email = lead_info.get('email', '')

                if lead_email:
                    # Email is available - make it VERY clear to the AI
                    context = f"""CONVERSATION CONTEXT:
You are speaking with: {lead_name}
Their email address on file: {lead_email}

🚨 IMPORTANT: You already have their email address ({lead_email}).
- DO NOT ask for it again
- DO NOT ask them to confirm it
- USE IT IMMEDIATELY when booking the meeting
- If they say "you already have it", they are correct - proceed with booking using {lead_email}"""
                else:
                    # Email not available - AI needs to ask for it
                    context = f"""CONVERSATION CONTEXT:
You are speaking with: {lead_name}
Their email address: NOT PROVIDED - you must ask for it before booking

⚠️ REQUIRED: You MUST ask for their email address before you can book a meeting."""

                messages.append({"role": "system", "content": context})

            # Add conversation history
            messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            logger.info(f"Sending to LLM with tools: {user_message[:100]}...")

            # Call OpenAI with function calling enabled
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tools_definition(),
                tool_choice="auto",  # Let model decide when to use tools
                temperature=0.7,
                max_tokens=200
            )

            assistant_message = response.choices[0].message
            tool_calls_data = []

            # Check if model wants to call any tools
            if assistant_message.tool_calls:
                logger.info(f"LLM wants to call {len(assistant_message.tool_calls)} tool(s)")

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    tool_result = await self._execute_tool(tool_name, tool_args)

                    tool_calls_data.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": tool_result
                    })

                    # Add tool result to conversation for LLM context
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result)
                    })

                # Get final response after tool execution
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=200
                )

                ai_response = final_response.choices[0].message.content.strip()

            else:
                # No tool calls, use direct response
                ai_response = assistant_message.content.strip() if assistant_message.content else "I'm here to help!"

            # Classify intent based on response and tool usage
            intent = self._classify_intent(ai_response, user_message, tool_calls_data)

            logger.info(f"LLM response ({intent}): {ai_response[:100]}...")

            return intent, ai_response, tool_calls_data if tool_calls_data else None

        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return ConversationIntent.END_CALL, "I apologize, but I'm having technical difficulties. Goodbye!", None

    def _classify_intent(
        self,
        ai_response: str,
        user_message: str,
        tool_calls: Optional[List[Dict]] = None
    ) -> str:
        """
        Classify conversation intent

        Args:
            ai_response: AI's text response
            user_message: User's message
            tool_calls: List of tool calls made (if any)

        Returns:
            Intent classification
        """
        ai_lower = ai_response.lower()
        user_lower = user_message.lower()

        # Check if meeting was booked AND AI is explicitly ending the call
        meeting_booked = False
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call["tool"] == "book_meeting" and tool_call["result"].get("success"):
                    meeting_booked = True
                    break

        # Goodbye phrases that signal conversation is ending
        goodbye_phrases = [
            "goodbye", "bye", "talk to you then", "see you then",
            "looking forward to our meeting", "have a great day",
            "thank you for your time", "speak to you soon", "catch you later"
        ]

        # Check if AI is saying goodbye
        ai_saying_goodbye = any(phrase in ai_lower for phrase in goodbye_phrases)

        # If meeting was booked AND AI is saying goodbye, end the call
        if meeting_booked and ai_saying_goodbye:
            return ConversationIntent.MEETING_BOOKED

        # If meeting was booked but AI is still asking questions, continue conversation
        if meeting_booked and not ai_saying_goodbye:
            # AI asking follow-up questions after booking - keep conversation going
            return ConversationIntent.SCHEDULE_MEETING

        # Check for explicit booking confirmation markers (without goodbye)
        if any(word in ai_lower for word in ["confirmed", "calendar invite sent"]) and ai_saying_goodbye:
            return ConversationIntent.MEETING_BOOKED

        # AI wants to end call without booking
        if ai_saying_goodbye:
            return ConversationIntent.END_CALL

        # User signals
        not_interested = ["not interested", "no thanks", "not now", "busy", "don't call", "remove me"]
        if any(keyword in user_lower for keyword in not_interested):
            return ConversationIntent.NOT_INTERESTED

        # Scheduling signals
        if tool_calls and any(tc["tool"] == "check_calendar_availability" for tc in tool_calls):
            return ConversationIntent.SCHEDULE_MEETING

        # Interested signals
        interested = ["yes", "sure", "okay", "interested", "tell me more"]
        if any(keyword in user_lower for keyword in interested):
            return ConversationIntent.INTERESTED

        # Questions = needs more info
        if "?" in user_message:
            return ConversationIntent.NEEDS_INFO

        return ConversationIntent.NEEDS_INFO

    async def summarize_call(
        self,
        transcript: str
    ) -> str:
        """
        Generate a summary of the call

        Args:
            transcript: Full conversation transcript as text

        Returns:
            Summary text
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a call summarization assistant. Summarize the following sales call in 2-3 sentences. Include the outcome (meeting booked, not interested, needs follow-up, etc.), key points discussed, and any actions taken (like checking calendar or booking meetings)."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this call transcript:\n\n{transcript}"
                }
            ]

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=150
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return "Call completed."
