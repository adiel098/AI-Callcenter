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

    def __init__(self, calendar_service=None):
        """
        Initialize LLM service with tool support

        Args:
            calendar_service: CalendarService instance for booking
        """
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"  # Fast and cost-effective
        self.system_prompt = self._load_system_prompt()

        # Services for executing tools
        self.calendar_service = calendar_service

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
- When user agrees to a time and provides their email, use book_meeting

IMPORTANT: Always collect the guest's email before booking!
Google Calendar will automatically send the invitation and reminders.
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
            logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

            if tool_name == "check_calendar_availability":
                return await self._check_calendar_availability(tool_args)

            elif tool_name == "book_meeting":
                return await self._book_meeting(tool_args)

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {str(e)}")
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
        if not self.calendar_service:
            logger.error("Calendar service not available")
            return {
                "success": False,
                "error": "Calendar service is not configured. Please contact support."
            }

        try:
            duration = args.get("duration_minutes", 30)
            num_slots = args.get("num_slots", 3)
            preferred_date = args.get("preferred_date", "tomorrow")

            # Parse the preferred date
            start_date = self._parse_date_string(preferred_date)
            logger.info(f"Checking availability from {start_date.date()} (user requested: {preferred_date})")

            # Calculate end date (2 weeks from preferred date)
            end_date = start_date + timedelta(days=14)

            # Get available slots from calendar service
            slots = self.calendar_service.get_available_slots(
                start_date=start_date,
                end_date=end_date,
                duration_minutes=duration
            )

            # Extract just the display strings for the LLM
            display_slots = [slot['display'] for slot in slots[:num_slots]]

            logger.info(f"Found {len(display_slots)} available slots")

            return {
                "success": True,
                "available_slots": display_slots
            }

        except Exception as e:
            logger.error(f"Error checking calendar availability: {e}")
            return {"success": False, "error": str(e)}

    async def _book_meeting(self, args: Dict) -> Dict:
        """
        Book a meeting on Google Calendar and send calendar invite via email.

        This method:
        1. Creates calendar event (without attendees to avoid service account restriction)
        2. Sends .ics calendar invite via email (works with any email provider)

        Args:
            args: Dictionary containing:
                - datetime: ISO format datetime string (required)
                - guest_email: Guest's email address (required)
                - guest_name: Guest's name (required)
                - duration_minutes: Meeting duration (default: 30)
                - meeting_title: Meeting title (default: "Sales Meeting")
                - description: Meeting description (optional)

        Returns:
            Dictionary with success status, event_id, and google_meet_link
        """
        if not self.calendar_service:
            logger.error("Calendar service not available for booking")
            return {
                "success": False,
                "error": "Calendar service is not configured. Please contact support."
            }

        try:
            from backend.services.email_service import EmailService

            # Validate and parse datetime
            try:
                meeting_datetime = datetime.fromisoformat(args["datetime"])
            except (ValueError, KeyError) as e:
                logger.error(f"Invalid datetime format: {args.get('datetime')}")
                return {
                    "success": False,
                    "error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                }

            duration = args.get("duration_minutes", 30)
            end_time = meeting_datetime + timedelta(minutes=duration)
            meeting_title = args.get("meeting_title", "Sales Meeting")
            meeting_description = args.get("description", f"Meeting with {args['guest_name']}")

            # Create meeting via calendar service (without attendees field)
            result = self.calendar_service.create_meeting(
                summary=meeting_title,
                start_time=meeting_datetime,
                end_time=end_time,
                attendee_email=args["guest_email"],  # Not added to calendar, used for reference
                description=meeting_description
            )

            if not result:
                return {"success": False, "error": "Failed to create calendar event"}

            event_id = result['event_id']
            google_meet_link = result.get('google_meet_link')

            # Send calendar invite via email
            try:
                email_service = EmailService()
                email_sent = email_service.send_calendar_invite(
                    attendee_email=args["guest_email"],
                    attendee_name=args["guest_name"],
                    meeting_datetime=meeting_datetime,
                    duration_minutes=duration,
                    meeting_title=meeting_title,
                    meeting_description=meeting_description,
                    google_meet_link=google_meet_link
                )

                if email_sent:
                    logger.info(f"Calendar invite emailed to {args['guest_email']}")
                    return {
                        "success": True,
                        "meeting_id": event_id,
                        "google_meet_link": google_meet_link,
                        "message": f"Meeting booked and calendar invite sent to {args['guest_email']}"
                    }
                else:
                    # Event created but email failed
                    logger.warning(f"Event {event_id} created but failed to send email invite")
                    return {
                        "success": True,
                        "meeting_id": event_id,
                        "google_meet_link": google_meet_link,
                        "warning": "Meeting created but failed to send email invitation"
                    }

            except Exception as email_error:
                logger.error(f"Failed to send calendar invite email: {email_error}")
                # Still return success since event was created
                return {
                    "success": True,
                    "meeting_id": event_id,
                    "google_meet_link": google_meet_link,
                    "warning": f"Meeting created but email service failed: {str(email_error)}"
                }

        except Exception as e:
            logger.error(f"Meeting booking error: {e}")
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
                context = f"Lead information: Name: {lead_info.get('name', 'Unknown')}"
                if lead_info.get('email'):
                    context += f", Email: {lead_info['email']}"
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
