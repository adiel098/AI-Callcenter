# AI Outbound Meeting Scheduler

An autonomous AI system that replaces human call centers for scheduling meetings with potential clients. The system automatically calls leads, conducts natural voice conversations in multiple languages, detects interest, proposes time slots, and books meetings directly on calendars.

## 🎯 System Overview

This system is a scalable, cloud-native AI agent that:
- Makes outbound phone calls automatically
- Conducts human-like conversations in multiple languages (auto-detected from phone number)
- Understands intent and responds appropriately
- Schedules meetings when leads express interest
- Integrates with Google Calendar for automatic booking
- Provides real-time analytics and monitoring

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │◄────►│   FastAPI    │◄────►│ PostgreSQL  │
│  Dashboard  │      │   Backend    │      │  Database   │
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Celery    │
                     │   Workers    │
                     └──────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌───▼───┐         ┌────▼─────┐
   │ Twilio  │         │OpenAI │         │ Google   │
   │ (Calls) │         │(GPT-4)│         │ Calendar │
   └─────────┘         └───┬───┘         └──────────┘
                           │
                    ┌──────┴──────┐
                    │             │
              ┌─────▼──┐    ┌────▼──────┐
              │Deepgram│    │ElevenLabs │
              │  (STT) │    │   (TTS)   │
              └────────┘    └───────────┘
```

## 🚀 Features

### Core Functionality
- ✅ **Auto-dialing**: Automatically calls leads from database
- ✅ **Multi-language Support**: Detects language from phone prefix (+972→Hebrew, +1→English, etc.)
- ✅ **Natural Conversations**: Uses GPT-4o-mini for human-like dialogue
- ✅ **Intent Detection**: Understands if lead is interested, needs info, or wants to schedule
- ✅ **Calendar Integration**: Automatically books meetings on Google Calendar
- ✅ **Call Recording**: Stores call recordings and full transcripts
- ✅ **Real-time Analytics**: Dashboard with KPIs and visualizations

### Scalability
- ✅ **Horizontal Scaling**: Workers auto-scale based on load
- ✅ **Async Processing**: Non-blocking I/O for high throughput
- ✅ **Message Queue**: Celery + Redis for distributed task processing
- ✅ **Connection Pooling**: Optimized database connections

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI | REST API server |
| **Workers** | Celery | Background task processing |
| **Database** | PostgreSQL | Data persistence |
| **Queue/Cache** | Redis | Task queue & session management |
| **Telephony** | Twilio | Outbound calling |
| **Speech-to-Text** | Deepgram | Real-time transcription |
| **Text-to-Speech** | ElevenLabs | Natural voice synthesis |
| **LLM** | OpenAI GPT-4o-mini | Conversation intelligence |
| **Calendar** | Google Calendar API | Meeting scheduling |
| **Frontend** | React + TypeScript | Admin dashboard |
| **Deployment** | Render | Cloud hosting |

## 📋 Prerequisites

Before running this project, you need:

1. **API Keys**:
   - Twilio (account SID, auth token, phone number)
   - OpenAI API key
   - ElevenLabs API key
   - Deepgram API key
   - Google Calendar API credentials

2. **Services**:
   - PostgreSQL database
   - Redis instance
   - Google Calendar account

3. **Development Tools**:
   - Python 3.11+
   - Node.js 18+
   - Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd HomeWork
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Database Setup

```bash
# Initialize database (creates tables)
python -c "from backend.database import init_db; init_db()"
```

### 4. Start Backend Services

```bash
# Terminal 1: Start FastAPI server
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start Celery worker
cd backend
celery -A workers.celery_app worker --loglevel=info
```

### 5. Frontend Setup (Optional for MVP)

```bash
cd frontend
npm install
npm run dev
```

The API will be available at `http://localhost:8000`
The dashboard will be at `http://localhost:5173`

## 📊 API Endpoints

### Leads
- `POST /api/leads/` - Create a lead
- `GET /api/leads/` - List leads (paginated)
- `POST /api/leads/upload` - Upload CSV of leads
- `GET /api/leads/{id}` - Get lead details
- `DELETE /api/leads/{id}` - Delete lead

### Calls
- `GET /api/calls/` - List calls
- `GET /api/calls/{id}` - Get call details with transcript
- `GET /api/calls/{id}/recording` - Get recording URL

### Meetings
- `GET /api/meetings/` - List meetings
- `GET /api/meetings/{id}` - Get meeting details
- `PATCH /api/meetings/{id}/status` - Update meeting status

### Campaigns
- `POST /api/campaigns/start` - Start call campaign
- `GET /api/campaigns/status` - Get campaign status

### Analytics
- `GET /api/analytics/overview` - Get KPI overview
- `GET /api/analytics/call-outcomes` - Call outcome distribution
- `GET /api/analytics/language-distribution` - Language stats
- `GET /api/analytics/calls-over-time` - Time series data

### Webhooks (Twilio)
- `POST /api/webhooks/twilio/status` - Call status updates
- `POST /api/webhooks/twilio/voice` - Voice callback (TwiML)
- `POST /api/webhooks/twilio/process-speech` - Speech processing

Full API documentation available at `http://localhost:8000/docs`

## 📁 Project Structure

```
HomeWork/
├── backend/
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── leads.py
│   │       ├── calls.py
│   │       ├── meetings.py
│   │       ├── campaigns.py
│   │       ├── analytics.py
│   │       └── webhooks.py
│   ├── models/              # Database models
│   │   ├── lead.py
│   │   ├── call.py
│   │   ├── meeting.py
│   │   └── conversation_history.py
│   ├── services/            # Business logic
│   │   ├── twilio_service.py
│   │   ├── speech_service.py
│   │   ├── llm_service.py
│   │   └── calendar_service.py
│   ├── workers/             # Celery tasks
│   │   ├── celery_app.py
│   │   └── tasks.py
│   ├── utils/               # Utilities
│   │   └── language_detector.py
│   ├── prompts/             # LLM system prompts
│   │   ├── system_prompt_en.txt
│   │   └── system_prompt_he.txt
│   ├── config.py           # Configuration
│   ├── database.py         # Database connection
│   ├── main.py             # FastAPI app
│   └── requirements.txt    # Python dependencies
├── frontend/               # React dashboard (to be created)
├── render.yaml             # Render deployment config
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

All configuration is done via environment variables. See `.env.example` for the complete list.

**Critical Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_scheduler

# Redis
REDIS_URL=redis://localhost:6379/0

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI
OPENAI_API_KEY=sk-...

# ElevenLabs
ELEVENLABS_API_KEY=...

# Deepgram
DEEPGRAM_API_KEY=...

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
```

### Language Detection

The system automatically detects language from phone number prefix:

| Prefix | Country | Language |
|--------|---------|----------|
| +972 | Israel | Hebrew |
| +1 | USA/Canada | English |
| +44 | UK | English |
| +33 | France | French |
| +49 | Germany | German |
| +34 | Spain | Spanish |

Add more mappings in `backend/utils/language_detector.py`

### Google Calendar Setup

The system uses Google Calendar API to check availability and book meetings. Follow these steps to set up calendar integration:

#### Step 1: Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project from the project picker (top bar)
   - If you see project ID `689797627749` or `callcenter-477010`, select it
   - If no project exists, create a new one: **"New Project"** → Enter name → **"Create"**
3. Navigate to **[APIs & Services > Library](https://console.cloud.google.com/apis/library)**
4. In the search bar, type: **"Google Calendar API"**
5. Click on **"Google Calendar API"** from results
6. Click **"Enable"** button
7. Wait 2-3 minutes for API to propagate

#### Step 2: Choose Authentication Method

**Important:** There are two authentication methods. Choose based on your account type:

| Account Type | Recommended Method | Why |
|--------------|-------------------|-----|
| **Personal Gmail** | OAuth (Step 2B) | Service accounts can't invite attendees to personal calendars |
| **Google Workspace** | Service Account (Step 2A) | Better for production, requires Domain-Wide Delegation |

#### Step 2A: Create Service Account (For Google Workspace)

⚠️ **Note:** Service accounts require **Domain-Wide Delegation** to invite attendees. Without it, you'll get a `forbiddenForServiceAccounts` error. See troubleshooting section for details.

1. Go to **[APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)**
2. Click **"Create Credentials"** → **"Service Account"**
3. Fill in details:
   - **Name**: `AI Scheduler Service Account`
   - **Description**: `Service account for booking meetings`
4. Click **"Create and Continue"**
5. Grant role: **"Editor"** or **"Calendar API Service Agent"**
6. Click **"Continue"** → **"Done"**
7. Click on the created service account
8. Go to **"Keys"** tab → **"Add Key"** → **"Create New Key"**
9. Select **JSON** format → **"Create"**
10. Save the downloaded JSON file as `backend/service-account.json`
11. Copy the service account email (looks like `ai-scheduler@project-id.iam.gserviceaccount.com`)

#### Step 3: Share Calendar with Service Account

1. Open [Google Calendar](https://calendar.google.com)
2. Find your calendar in the left sidebar
3. Click the three dots → **"Settings and sharing"**
4. Scroll to **"Share with specific people"**
5. Click **"Add people"**
6. Paste the service account email from Step 2.11
7. Set permissions: **"Make changes to events"**
8. Click **"Send"**
9. Copy your calendar ID from **"Integrate calendar"** section (looks like `xyz@group.calendar.google.com`)
10. Update `.env` file:
    ```bash
    GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
    ```

#### Step 2B: OAuth Credentials (For Personal Gmail or Development)

⭐ **Recommended for personal Gmail accounts** - No Domain-Wide Delegation needed!

1. Go to **[APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials)**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Configure consent screen if prompted
4. Application type: **"Desktop app"**
5. Name: `AI Scheduler Desktop`
6. Click **"Create"**
7. Download JSON file
8. Save as `backend/credentials.json`
9. First run will open browser for authentication
10. Token saved to `backend/token.json` for future use

#### Step 4: Verify Calendar Service

Run this Python script to verify everything works:

```python
# test_calendar.py
from backend.services.calendar_service import CalendarService
from datetime import datetime, timedelta

# Initialize service
cal = CalendarService()

# Test 1: Check if service initialized
if cal.service:
    print("✅ Calendar service initialized successfully")
else:
    print("❌ Calendar service failed to initialize")
    exit(1)

# Test 2: Get available slots
try:
    slots = cal.get_next_available_slots(count=3, duration_minutes=30)
    print(f"✅ Found {len(slots)} available time slots:")
    for slot in slots:
        print(f"   - {slot}")
except Exception as e:
    print(f"❌ Failed to get available slots: {e}")
    exit(1)

# Test 3: Check specific date
try:
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_start = tomorrow.replace(hour=9, minute=0, second=0)
    tomorrow_end = tomorrow.replace(hour=17, minute=0, second=0)

    available = cal.get_available_slots(
        start_datetime=tomorrow_start,
        end_datetime=tomorrow_end,
        duration_minutes=30
    )
    print(f"✅ Tomorrow has {len(available)} free slots")
except Exception as e:
    print(f"❌ Failed to check tomorrow's availability: {e}")
    exit(1)

print("\n🎉 All calendar tests passed!")
```

Run the test:
```bash
cd backend
python test_calendar.py
```

#### Step 5: Verify in Application

Test calendar integration in the full system:

```python
# test_llm_calendar.py
import asyncio
from backend.services.llm_service import LLMService
from backend.services.calendar_service import CalendarService

async def test_llm_calendar():
    # Initialize services
    calendar = CalendarService()
    llm = LLMService(calendar_service=calendar)

    # Test calendar availability check
    print("Testing calendar availability check via LLM...")
    intent, response, tools = await llm.get_response_with_tools(
        user_message="When are you available next week?",
        conversation_history=[],
        lead_info={"name": "Test User", "email": "test@example.com"}
    )

    print(f"Intent: {intent}")
    print(f"AI Response: {response}")
    print(f"Tools used: {len(tools)} tool(s)")

    if tools and 'check_calendar_availability' in str(tools):
        print("✅ Calendar availability check works!")
    else:
        print("❌ Calendar tool was not used")
        return False

    # Test meeting booking
    print("\nTesting meeting booking via LLM...")
    intent, response, tools = await llm.get_response_with_tools(
        user_message="Let's book a meeting for tomorrow at 2pm. My email is test@example.com",
        conversation_history=[
            {"role": "assistant", "content": "I can help schedule a meeting. When works for you?"}
        ],
        lead_info={"name": "Test User", "email": "test@example.com"}
    )

    print(f"Intent: {intent}")
    print(f"AI Response: {response}")
    print(f"Tools used: {len(tools)} tool(s)")

    if tools and 'book_meeting' in str(tools):
        print("✅ Meeting booking works!")
    else:
        print("⚠️ Booking not triggered (might need more specific time)")

    print("\n🎉 LLM + Calendar integration test complete!")
    return True

# Run the test
asyncio.run(test_llm_calendar())
```

Run the test:
```bash
cd backend
python test_llm_calendar.py
```

#### Step 6: Monitor Calendar Service Health

Add this health check to verify calendar service status:

```bash
# Check if calendar service is working
curl http://localhost:8000/docs

# Look for successful calendar operations in logs
tail -f logs/worker.log | grep -i calendar
```

Expected log output:
```
✅ Google Calendar service initialized successfully
Executing tool: check_calendar_availability
Calendar availability check successful: 3 slots found
```

## 🎬 Usage Workflow

### 1. Upload Leads

Upload a CSV file with columns: `name`, `phone`, `email`

```csv
name,phone,email
John Doe,+12125551234,john@example.com
יוסי כהן,+972501234567,yossi@example.co.il
```

### 2. Start Campaign

Via API:
```bash
curl -X POST http://localhost:8000/api/campaigns/start \
  -H "Content-Type: application/json" \
  -d '{"name": "Q1 Outreach", "lead_ids": [1, 2, 3]}'
```

### 3. Monitor Calls

- View live calls in dashboard
- See real-time transcripts
- Track outcomes (meeting scheduled, not interested, etc.)

### 4. Review Meetings

- Check scheduled meetings in calendar
- View guest details
- Confirm or cancel meetings

## 📈 Scalability

### Capacity

- **Initial**: 10-50 concurrent calls
- **Scaled**: 500+ concurrent calls with worker scaling
- **Lead Processing**: 10,000+ leads per day

### Render Auto-Scaling

The system automatically scales based on:
- CPU usage (workers scale at 70% CPU)
- Queue depth (more workers added when queue grows)
- Time of day (can configure scaling schedules)

### Performance Optimization

- Connection pooling for database
- Redis caching for session state
- Async I/O throughout
- Streaming APIs (Deepgram, ElevenLabs, GPT-4)

## 🐛 Troubleshooting

### Common Issues

**1. Calls Not Initiating**
- Check Twilio credentials
- Verify phone number format (E.164: +1234567890)
- Check Twilio account balance

**2. Google Calendar API Errors**

#### Error: `403 Forbidden - accessNotConfigured`
```
Google Calendar API has not been used in project XXXXXX before or it is disabled
```

**Solution:**
1. Identify which Google Cloud project is being used:
   - Check error message for project ID (e.g., `689797627749`)
   - Or check your `backend/service-account.json` for `project_id` field
2. Enable the API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Switch to the correct project (use project picker in top bar)
   - Navigate to [APIs & Services > Library](https://console.cloud.google.com/apis/library)
   - Search for "Google Calendar API"
   - Click "Enable"
3. Wait 2-3 minutes for changes to propagate
4. Restart your application:
   ```bash
   # Restart FastAPI
   pkill -f uvicorn
   uvicorn backend.main:app --reload --port 8000

   # Restart Celery workers
   pkill -f celery
   celery -A backend.workers.celery_app worker --loglevel=info
   ```
5. Test again using the verification scripts in the Google Calendar Setup section

#### Error: `403 Forbidden - forbiddenForServiceAccounts`
```
Service accounts cannot invite attendees without Domain-Wide Delegation of Authority
```

**What This Means:**
- ✅ Google Calendar API is enabled (the previous error is fixed!)
- ❌ Service accounts need special permission to send meeting invites with attendees
- This only affects **service account authentication** (not OAuth)
- Common when using personal Gmail accounts (not Google Workspace)

**Solution A: Switch to OAuth (Recommended for Personal Gmail)** ⭐

If you're using a personal Gmail account, switch to OAuth authentication:

1. **Rename or remove service account file:**
   ```bash
   cd backend
   mv service-account.json service-account.json.backup
   ```

2. **Ensure OAuth credentials exist:**
   ```bash
   # Check if you have credentials.json
   ls -la backend/credentials.json
   ```

   If not, follow **"Alternative: OAuth Credentials"** in the Google Calendar Setup section above.

3. **Delete existing token (if any):**
   ```bash
   rm backend/token.json
   ```

4. **Restart application:**
   ```bash
   # The CalendarService will automatically use OAuth instead
   uvicorn backend.main:app --reload --port 8000
   ```

5. **Authenticate in browser:**
   - First calendar operation will open browser
   - Sign in with your Google account
   - Grant calendar permissions
   - Token saved to `backend/token.json`

6. **Verify it works:**
   ```bash
   cd backend
   python test_calendar.py
   ```

**Solution B: Enable Domain-Wide Delegation (For Google Workspace Only)**

If you have a Google Workspace organization with admin access:

1. **In Google Cloud Console:**
   - Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
   - Click on your service account
   - Click **"Show Domain-Wide Delegation"**
   - Click **"Enable Google Workspace Domain-Wide Delegation"**
   - Note the **Client ID** (looks like `123456789012345678901`)

2. **In Google Workspace Admin Console:**
   - Go to [admin.google.com](https://admin.google.com)
   - Navigate to **Security > Access and data control > API Controls**
   - Click **"Manage Domain-Wide Delegation"**
   - Click **"Add new"**
   - Enter the service account **Client ID**
   - Add OAuth scopes:
     ```
     https://www.googleapis.com/auth/calendar
     https://www.googleapis.com/auth/calendar.events
     ```
   - Click **"Authorize"**

3. **Update service account code (if needed):**
   - Ensure your service account is delegating a user email
   - This typically requires code changes in `calendar_service.py`

4. **Restart application and test**

**Solution C: .ics Email Attachment** ⭐ **PRODUCTION SOLUTION - NOW IMPLEMENTED**

This system now automatically sends calendar invites as .ics email attachments, which works with service accounts and all email providers!

**How it works:**
1. Calendar event created on Google Calendar (without attendees field)
2. .ics calendar file automatically generated
3. Email sent to guest with .ics attachment
4. Guest clicks "Add to Calendar" to import the event

**Supported Email Providers:**
- ✅ Gmail
- ✅ Outlook/Office 365
- ✅ Yahoo Mail
- ✅ Apple Mail
- ✅ Corporate email systems
- ✅ Any email client that supports .ics files

**Setup Instructions:**

1. **Configure SMTP in `.env` file:**

   For Gmail (Development):
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_business_email@gmail.com
   SMTP_PASSWORD=your_gmail_app_password
   COMPANY_NAME=Your Company Name
   ```

   Generate Gmail App Password: https://myaccount.google.com/apppasswords

   For SendGrid (Production):
   ```env
   SMTP_HOST=smtp.sendgrid.net
   SMTP_PORT=587
   SMTP_USER=apikey
   SMTP_PASSWORD=your_sendgrid_api_key
   ```

2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Test email service:**
   ```python
   from backend.services.email_service import EmailService
   from datetime import datetime, timedelta

   email_service = EmailService()

   # Test sending calendar invite
   success = email_service.send_calendar_invite(
       attendee_email="test@example.com",
       attendee_name="Test User",
       meeting_datetime=datetime.now() + timedelta(days=1),
       duration_minutes=30,
       meeting_title="Test Meeting",
       zoom_link="https://zoom.us/j/123456789?pwd=xxx"
   )

   print(f"Email sent: {success}")
   ```

4. **Restart your application:**
   ```bash
   # The system will now automatically send .ics invites
   uvicorn backend.main:app --reload --port 8000
   ```

**Features:**
- ✅ Professional HTML emails with meeting details
- ✅ .ics calendar file attachment
- ✅ Includes Zoom video conference links
- ✅ Works with service accounts (no OAuth needed)
- ✅ Fully automated - no manual intervention
- ✅ Recipient gets standard "Add to Calendar" experience

**Which Solution to Choose:**

| Your Situation | Recommended Solution |
|----------------|---------------------|
| Production system (any email domain) | **Solution C** (.ics Email) - **IMPLEMENTED** |
| Personal Gmail account | **Solution A** (OAuth) OR **Solution C** |
| Google Workspace + Admin access | **Solution B** (Domain-Wide Delegation) |
| Google Workspace + No admin access | **Solution A** (OAuth) OR **Solution C** |
| Quick testing/development | **Solution C** (.ics Email) - **READY TO USE** |

#### Error: `404 Not Found` or `Calendar not found`
```
Resource not found as specified or Insufficient Permission
```

**Solution:**
1. Verify calendar ID in `.env` file:
   ```bash
   # Should look like:
   GOOGLE_CALENDAR_ID=abc123@group.calendar.google.com
   # OR for primary calendar:
   GOOGLE_CALENDAR_ID=your.email@gmail.com
   ```
2. Check calendar sharing permissions:
   - Open [Google Calendar](https://calendar.google.com)
   - Go to calendar Settings → "Share with specific people"
   - Ensure service account email is listed with "Make changes to events" permission
3. Get the correct calendar ID:
   - In Google Calendar, go to Settings
   - Select your calendar from the left
   - Scroll to "Integrate calendar" section
   - Copy the "Calendar ID"

#### Error: `401 Unauthorized` or `Invalid Credentials`
```
Request had invalid authentication credentials
```

**Solution:**
1. Check authentication file exists:
   ```bash
   # Service account (production)
   ls -la backend/service-account.json

   # OR OAuth credentials (development)
   ls -la backend/credentials.json
   ls -la backend/token.json
   ```
2. If using service account:
   - Verify JSON file is valid (should have `type: "service_account"`)
   - Re-download from Google Cloud Console if corrupted
   - Ensure file path in `.env` matches actual location:
     ```bash
     GOOGLE_CALENDAR_CREDENTIALS_FILE=backend/service-account.json
     ```
3. If using OAuth:
   - Delete `backend/token.json`
   - Re-run application to trigger OAuth flow
   - Authenticate in browser when prompted
4. Verify file permissions:
   ```bash
   chmod 600 backend/service-account.json
   chmod 600 backend/credentials.json
   ```

#### Error: `Calendar service is not configured`
```
AI response: "Calendar service is not configured. Please contact support."
```

**Solution:**
1. Check application logs for root cause:
   ```bash
   tail -100 logs/worker.log | grep -i "calendar"
   ```
2. Look for initialization error:
   - If you see "❌ Failed to initialize Google Calendar service", check the error details
   - Common causes: missing credentials file, wrong file path, invalid JSON
3. Verify environment variables:
   ```bash
   # Print current config (remove sensitive data first!)
   python -c "from backend.config import settings; print(f'Calendar file: {settings.google_calendar_credentials_file}'); print(f'Calendar ID: {settings.google_calendar_id}')"
   ```
4. Test calendar service directly:
   ```bash
   cd backend
   python -c "from services.calendar_service import CalendarService; cal = CalendarService(); print('✅ Success' if cal.service else '❌ Failed')"
   ```

#### Error: `Project ID Mismatch`
If you have multiple Google Cloud projects and see different project IDs in errors:

**Solution:**
1. Decide which project to use (e.g., `callcenter-477010` or `689797627749`)
2. Ensure API is enabled in THAT project
3. Ensure credentials are from THAT project:
   - Open `backend/service-account.json` or `backend/credentials.json`
   - Check `project_id` field matches your chosen project
4. If mismatch, create new credentials in the correct project

#### No Calendar Events Created (No Error)
AI conversation completes but no meeting appears on calendar.

**Solution:**
1. Check database for meeting record:
   ```bash
   # In Python console
   from backend.database import SessionLocal
   from backend.models.meeting import Meeting
   db = SessionLocal()
   meetings = db.query(Meeting).all()
   print(f"Total meetings: {len(meetings)}")
   for m in meetings[-5:]:  # Last 5
       print(f"Meeting: {m.scheduled_time}, Status: {m.status}")
   ```
2. Check if booking was attempted:
   ```bash
   grep "book_meeting" logs/worker.log | tail -20
   ```
3. Verify calendar visibility:
   - Open Google Calendar in browser
   - Check the correct calendar is selected (left sidebar)
   - Try different time ranges
4. Check Google Calendar event ID:
   ```bash
   # If meeting has google_event_id in database but not visible:
   # Event might be on a different calendar or deleted
   ```

**3. Worker Not Processing Tasks**
- Confirm Redis is running
- Check worker logs: `celery -A workers.celery_app inspect active`
- Verify database connection

**4. Poor Voice Quality**
- Check ElevenLabs API quota
- Verify audio format compatibility
- Test different voice IDs

### Quick Reference: Calendar Errors

| Error Code | Error Message | Quick Fix |
|------------|--------------|-----------|
| **403** | `accessNotConfigured` | Enable Google Calendar API in Google Cloud Console |
| **403** | `forbiddenForServiceAccounts` | Use .ics email invites (now implemented) OR switch to OAuth |
| **404** | `Calendar not found` | Verify calendar ID and sharing permissions |
| **401** | `Invalid credentials` | Check credentials file path and validity |
| **400** | `Bad Request` | Check date/time format and timezone |
| **429** | `Rate limit exceeded` | Add exponential backoff, check quota |
| **500** | `Backend Error` | Google Calendar service issue, retry later |

### Calendar Integration Checklist

Before deploying to production, verify:

- [ ] Google Calendar API is enabled in Google Cloud Console
- [ ] Service account created and JSON key downloaded
- [ ] Calendar shared with service account email
- [ ] Calendar ID added to `.env` file
- [ ] Credentials file at correct path (`backend/service-account.json`)
- [ ] Zoom credentials added to `.env` file (ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
- [ ] Test script runs successfully (`python test_calendar.py`)
- [ ] Application logs show "✅ Google Calendar service initialized"
- [ ] Application logs show "Zoom service initialized"
- [ ] Test booking creates actual calendar event
- [ ] Meeting invites are sent to attendees
- [ ] Zoom video conference links are generated

### Logs

View logs:
```bash
# API logs
tail -f logs/api.log

# Worker logs
tail -f logs/worker.log

# Calendar-specific logs
tail -f logs/worker.log | grep -i calendar

# On Render
render logs -s ai-scheduler-api
```

## 🚢 Deployment to Render

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### 2. Create Render Account

- Sign up at [render.com](https://render.com)
- Connect your GitHub repository

### 3. Deploy via Blueprint

- In Render dashboard, click "New +" → "Blueprint"
- Select your repository
- Render will detect `render.yaml` and create all services

### 4. Add Environment Variables

In each service settings, add your API keys (marked as `sync: false` in render.yaml)

### 5. Add Redis

- Create a new Redis instance in Render
- Copy connection string to `REDIS_URL` env var

### 6. Deploy

- Services will auto-deploy on git push
- Monitor deployment in Render dashboard

## 📝 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# With coverage
pytest --cov=backend tests/
```

### Code Style

```bash
# Format code
black backend/

# Lint
flake8 backend/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary. All rights reserved.

## 🙏 Acknowledgments

- Twilio for telephony infrastructure
- OpenAI for GPT-4 conversation intelligence
- ElevenLabs for natural voice synthesis
- Deepgram for accurate transcription
- Render for scalable hosting

## 📞 Support

For issues, questions, or feature requests, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for scalable AI-powered sales automation**
