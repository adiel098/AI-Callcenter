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

from backend.config import get_settings

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
        """Load the base system prompt from file"""
        prompts_dir = Path(__file__).parent.parent / "prompts"
        prompt_path = prompts_dir / "system_prompt_en.txt"

        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        # Fallback if file doesn't exist
        return "You are a professional AI assistant scheduling meetings."

    def _get_system_prompt_with_tools(self) -> str:
        """Get system prompt enhanced with tool instructions"""
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
        return self.system_prompt + tool_instructions

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

    async def _check_calendar_availability(self, args: Dict) -> Dict:
        """Check calendar availability and return free slots"""
        if not self.calendar_service:
            # Mock response for testing without calendar
            return {
                "success": True,
                "available_slots": [
                    {"datetime": "2025-01-10T14:00:00", "display": "Friday, January 10 at 2:00 PM"},
                    {"datetime": "2025-01-10T16:00:00", "display": "Friday, January 10 at 4:00 PM"},
                    {"datetime": "2025-01-13T10:00:00", "display": "Monday, January 13 at 10:00 AM"}
                ]
            }

        try:
            duration = args.get("duration_minutes", 30)
            num_slots = args.get("num_slots", 3)

            # Get available slots from calendar service
            slots = self.calendar_service.get_next_available_slots(
                count=num_slots,
                duration_minutes=duration
            )

            return {
                "success": True,
                "available_slots": slots
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _book_meeting(self, args: Dict) -> Dict:
        """Book a meeting on Google Calendar"""
        if not self.calendar_service:
            # Mock response for testing
            return {
                "success": True,
                "meeting_id": "mock_meeting_123",
                "calendar_link": "https://calendar.google.com/event?eid=mock123",
                "message": f"Meeting booked for {args.get('guest_name')} at {args.get('datetime')}"
            }

        try:
            meeting_datetime = datetime.fromisoformat(args["datetime"])
            duration = args.get("duration_minutes", 30)
            end_time = meeting_datetime + timedelta(minutes=duration)

            # Create meeting via calendar service
            event_id = self.calendar_service.create_meeting(
                summary=args.get("meeting_title", "Sales Meeting"),
                start_time=meeting_datetime,
                end_time=end_time,
                attendee_email=args["guest_email"],
                description=f"Meeting with {args['guest_name']}"
            )

            if event_id:
                return {
                    "success": True,
                    "meeting_id": event_id,
                    "calendar_link": f"https://calendar.google.com/calendar/event?eid={event_id}",
                    "message": f"Successfully booked meeting for {args['guest_name']}"
                }
            else:
                return {"success": False, "error": "Failed to create calendar event"}

        except Exception as e:
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
        # If meeting was booked via tool, that's the intent
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call["tool"] == "book_meeting" and tool_call["result"].get("success"):
                    return ConversationIntent.MEETING_BOOKED

        ai_lower = ai_response.lower()
        user_lower = user_message.lower()

        # Check for explicit markers
        if any(word in ai_lower for word in ["booked", "confirmed", "scheduled", "calendar invite"]):
            return ConversationIntent.MEETING_BOOKED

        if any(word in ai_lower for word in ["goodbye", "thank you for your time", "have a great day"]):
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
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate a summary of the call

        Args:
            conversation_history: Full conversation

        Returns:
            Summary text
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Summarize this sales call in 2-3 sentences. Include outcome and any tools used."
                }
            ]
            messages.extend(conversation_history)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return "Call completed."
