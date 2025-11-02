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

**2. No Calendar Events Created**
- Verify Google Calendar credentials
- Check calendar ID
- Ensure API is enabled in Google Cloud Console

**3. Worker Not Processing Tasks**
- Confirm Redis is running
- Check worker logs: `celery -A workers.celery_app inspect active`
- Verify database connection

**4. Poor Voice Quality**
- Check ElevenLabs API quota
- Verify audio format compatibility
- Test different voice IDs

### Logs

View logs:
```bash
# API logs
tail -f logs/api.log

# Worker logs
tail -f logs/worker.log

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
