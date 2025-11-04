# 🤖 AI Outbound Meeting Scheduler

> **Replace Your Call Center with AI** - Autonomous system that makes outbound calls, conducts natural conversations, and books meetings automatically.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178c6.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📸 Screenshots

<table>
  <tr>
    <td width="50%">
      <img src="screenshots/dashboard_page.png" alt="Dashboard Overview" />
      <p align="center"><b>Dashboard Overview</b><br/>Real-time metrics and campaign insights</p>
    </td>
    <td width="50%">
      <img src="screenshots/analytics_page.png" alt="Analytics & Reports" />
      <p align="center"><b>Analytics & Reports</b><br/>Comprehensive campaign performance data</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="screenshots/call_transcript.png" alt="AI Conversation" />
      <p align="center"><b>AI Conversation Transcript</b><br/>Natural dialogue with real-time processing</p>
    </td>
    <td width="50%">
      <img src="screenshots/meeting_page.png" alt="Meeting Management" />
      <p align="center"><b>Meeting Management</b><br/>Track all scheduled meetings and status</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="screenshots/setting_page.png" alt="Customizable AI" />
      <p align="center"><b>Customizable AI Prompts</b><br/>Configure your AI agent behavior</p>
    </td>
    <td width="50%">
      <img src="screenshots/api_page.png" alt="API Documentation" />
      <p align="center"><b>API Documentation</b><br/>Partner integration with code examples</p>
    </td>
  </tr>
</table>

---

## ✨ Key Features

- 🤖 **OpenAI Function Calling** - AI doesn't just talk, it takes action: checks calendars, books meetings, sends emails
- 📞 **Autonomous Outbound Calling** - Fully automated call initiation and handling via Twilio
- 💬 **Natural Conversations** - Real-time speech-to-text and text-to-speech for human-like interactions
- 📅 **Smart Calendar Integration** - Automatically books meetings on Google Calendar based on availability
- 🎥 **Zoom Meeting Links** - Generates video conferencing links automatically
- 🌍 **Multi-Language Support** - Auto-detects language from phone number prefix
- 📊 **Comprehensive Dashboard** - Beautiful React interface with real-time analytics
- ⚡ **Production-Ready Scalability** - Celery workers, PostgreSQL, Redis queue, auto-scaling on Render
- 🔒 **Secure & Reliable** - OAuth authentication, webhook verification, error handling
- 📈 **Advanced Analytics** - Track conversion rates, call outcomes, and campaign performance

---

## 🔄 How It Works

```mermaid
graph TD
    A[1. Lead Upload] --> B[Database]
    B --> C[2. Campaign Started]
    C --> D[Celery Worker Queues Call]
    D --> E[3. Twilio Makes Outbound Call]
    E --> F[Lead's Phone Rings]
    F --> G[4. User Speaks]
    G --> H[Twilio Transcribes - Real-time STT]
    H --> I[5. GPT-4o-mini Processes]
    I --> J{AI Decision Engine}
    J -->|Check Calendar| K[check_calendar_availability]
    J -->|Book Meeting| L[book_meeting]
    K --> M[6. AI Generates Response]
    L --> M
    M --> N[Twilio TTS]
    N --> O[7. User Hears Response]
    O --> P{Meeting Booked?}
    P -->|No| G
    P -->|Yes| Q[9. Save to Database]
    Q --> R[Google Calendar Invite]
    Q --> S[Analytics Updated]

    style A fill:#e1f5ff
    style I fill:#fff4e1
    style Q fill:#e8f5e9
```

### Example Conversation Flow

```
👤 User: "I'm interested. When are you available?"
   ↓
🤖 AI: [Calls check_calendar_availability()]
   → Returns: ["Tuesday 2pm", "Wednesday 10am"]

🤖 AI: "I have Tuesday at 2pm or Wednesday at 10am. Which works better for you?"
   ↓
👤 User: "Tuesday at 2pm works. My email is john@example.com"
   ↓
🤖 AI: [Calls book_meeting("2025-01-07T14:00", "john@example.com")]
   → Creates Google Calendar event
   → Generates Zoom link
   → Sends confirmation email

🤖 AI: "Perfect! I've booked our meeting for Tuesday at 2pm.
       You'll receive a calendar invite shortly at john@example.com."
   ↓
✅ Meeting successfully scheduled!
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109 (Python)
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Task Queue**: Celery 5.3 + Redis 5.0
- **AI/LLM**: OpenAI GPT-4o-mini with Function Calling
- **Telephony**: Twilio 8.11 (built-in STT/TTS)
- **Integrations**:
  - Google Calendar API (OAuth 2.0)
  - Zoom API (meeting generation)
- **Monitoring**: Sentry SDK

### Frontend
- **Framework**: React 18.2 + TypeScript 5.2
- **Build Tool**: Vite 5.0
- **UI Components**: Radix UI + Tailwind CSS 3.4
- **UI Library**: shadcn/ui components
- **State Management**: TanStack React Query 5.17
- **Forms**: React Hook Form 7.66
- **Charts**: Recharts 2.10
- **HTTP Client**: Axios 1.6

### DevOps & Deployment
- **Platform**: Render (auto-scaling)
- **Services**: Web (API) + Worker (Celery) + Static Site (Frontend)
- **Database**: Managed PostgreSQL
- **Cache**: Redis (Celery queue)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Dashboard (Frontend)               │
│  Dashboard │ Leads │ Calls │ Meetings │ Analytics │ Settings│
└────────────────────────────┬────────────────────────────────┘
                             │ REST API
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (API Layer)                │
│   /leads │ /calls │ /meetings │ /campaigns │ /webhooks      │
└────────────────────────────┬────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                ↓            ↓            ↓
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │PostgreSQL│  │  Redis   │  │  Celery  │
         │ Database │  │  Queue   │  │ Workers  │
         └──────────┘  └──────────┘  └────┬─────┘
                                           │
                    ┌──────────────────────┼──────────────────┐
                    ↓                      ↓                  ↓
            ┌──────────────┐      ┌──────────────┐   ┌──────────────┐
            │ LLM Service  │      │   Twilio     │   │   Google     │
            │  (GPT-4o)    │◄────►│   Service    │   │   Calendar   │
            │+ Function    │      │ (Calls/STT/  │   │   + Zoom     │
            │  Calling     │      │     TTS)     │   │              │
            └──────────────┘      └──────────────┘   └──────────────┘
```

### Key Components

- **API Layer**: REST endpoints for CRUD operations
- **Workers**: Background task processing for calls
- **LLM Service**: Conversation management with function calling
- **Twilio Service**: Call orchestration and audio processing
- **Calendar Service**: Meeting scheduling and availability checks
- **Database**: Persistent storage for leads, calls, meetings

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **PostgreSQL** (local or hosted)
- **Redis** (local or hosted)
- API Keys:
  - OpenAI API key
  - Twilio account (SID, Auth Token, Phone Number)
  - Google Calendar credentials
  - (Optional) Zoom API credentials

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-outbound-scheduler.git
cd ai-outbound-scheduler
```

#### 2. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp ../.env.example .env

# Edit .env with your API keys
# DATABASE_URL=postgresql://user:pass@localhost/dbname
# REDIS_URL=redis://localhost:6379/0
# OPENAI_API_KEY=sk-...
# TWILIO_ACCOUNT_SID=...
# TWILIO_AUTH_TOKEN=...
# TWILIO_PHONE_NUMBER=+1...

# Initialize database
python init_db.py

# Run the API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Start Celery Worker (separate terminal)

```bash
cd backend
celery -A workers.celery_app worker --loglevel=info
```

#### 4. Frontend Setup (separate terminal)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

#### 5. Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
HomeWork/
├── backend/
│   ├── api/
│   │   └── routes/          # REST API endpoints
│   │       ├── leads.py     # Lead management & CSV upload
│   │       ├── calls.py     # Call history & transcripts
│   │       ├── meetings.py  # Meeting CRUD operations
│   │       ├── campaigns.py # Campaign management
│   │       ├── analytics.py # KPIs and metrics
│   │       ├── webhooks.py  # Twilio callbacks
│   │       └── partners.py  # Partner management
│   ├── models/              # SQLAlchemy database models
│   │   ├── lead.py
│   │   ├── call.py
│   │   ├── meeting.py
│   │   └── conversation_history.py
│   ├── services/            # Business logic layer
│   │   ├── llm_service.py   # GPT-4o + Function Calling
│   │   ├── calendar_service.py  # Google Calendar integration
│   │   ├── twilio_service.py    # Twilio API wrapper
│   │   └── zoom_service.py      # Zoom meeting generation
│   ├── workers/             # Celery background tasks
│   │   ├── celery_app.py
│   │   └── tasks.py         # Call processing logic
│   ├── utils/               # Helper functions
│   │   └── language_detector.py
│   ├── prompts/
│   │   └── system_prompt_en.txt  # AI conversation prompt
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Leads.tsx
│   │   │   ├── Calls.tsx
│   │   │   ├── Meetings.tsx
│   │   │   └── Analytics.tsx
│   │   ├── components/      # Reusable components
│   │   │   └── ui/          # shadcn/ui components
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
├── screenshots/             # UI screenshots
├── .env.example             # Environment template
├── render.yaml              # Render deployment config
└── README.md
```

---

## ☁️ Deployment (Render)

This project is configured for one-click deployment on Render.

### Deploy to Render

1. **Push to GitHub**
2. **Connect to Render**: Link your repository
3. **Render will auto-detect** `render.yaml` and create:
   - Web Service (FastAPI API) - Auto-scales 1-10 instances
   - Worker Service (Celery) - Auto-scales 2-20 instances
   - Static Site (React Frontend) - CDN-backed
   - PostgreSQL Database (managed)
   - Redis Instance (managed)

4. **Set Environment Variables** in Render dashboard:
   - `OPENAI_API_KEY`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `GOOGLE_CALENDAR_CREDENTIALS` (as JSON string)

### Scaling Configuration

- **API Server**: Scales based on CPU/memory (1-10 instances)
- **Celery Workers**: Scales based on queue depth (2-20 instances)
- **Database**: Connection pooling for high concurrency
- **Cost**: ~$0.05 per successful booking

---

## 📚 API Documentation

### Interactive API Docs

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/leads` | POST | Upload leads (CSV or JSON) |
| `/api/leads/{id}` | GET | Get lead details |
| `/api/campaigns` | POST | Start outbound campaign |
| `/api/calls` | GET | List all calls with filters |
| `/api/calls/{id}/transcript` | GET | Get call transcript |
| `/api/meetings` | GET | List scheduled meetings |
| `/api/analytics/kpis` | GET | Get campaign KPIs |
| `/webhooks/twilio/voice` | POST | Twilio voice webhook |

### Partner API Integration

The system supports multi-tenant partner integration. See [API Documentation page](screenshots/api_page.png) for code examples in Python, JavaScript, and cURL.

---

## 🔍 Features Deep Dive

### 1. Dashboard & Real-Time Metrics
- Live call statistics
- Conversion rate tracking
- Active campaign monitoring
- Lead status distribution
- Recent activity feed

### 2. AI Conversation Management
- Customizable system prompts
- Function calling for calendar actions
- Context-aware responses
- Multi-turn conversation handling
- Automatic transcript generation

### 3. Meeting Scheduling
- Google Calendar integration
- Availability checking
- Automatic Zoom link generation
- Email confirmations
- Meeting status tracking

### 4. Analytics & Reporting
- Call outcome distribution
- Language performance metrics
- Conversion funnel analysis
- Voice performance stats
- Campaign ROI tracking

---

## 📈 Performance Metrics

### Latency
- **Speech-to-Text**: 200-500ms (Twilio)
- **LLM Processing**: 500-1500ms (OpenAI GPT-4o-mini)
- **Text-to-Speech**: 500-1000ms (Twilio)
- **Total Response Time**: ~2-4 seconds per conversation turn

### Cost per Call
- **Twilio**: $0.02 (2-minute call)
- **OpenAI**: $0.015 (with function calling)
- **Total**: ~$0.05 per successful booking

### Scalability
- **Initial**: 10-50 concurrent calls
- **Scaled**: 500+ concurrent calls
- **Daily Capacity**: 10,000+ leads processed

---

## 📖 Documentation

- **[COMPLETE_PROJECT_DOCUMENTATION.md](Documentation/COMPLETE_PROJECT_DOCUMENTATION.md)** - Comprehensive technical documentation (114KB)
- **[CLAUDE.md](Documentation/CLAUDE.md)** - Project instructions and architecture overview
- **[MIGRATION_TO_POSTGRESQL.md](Documentation/MIGRATION_TO_POSTGRESQL.md)** - Database migration guide
- **[.env.example](.env.example)** - Environment variables with detailed comments

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Code Standards
- **Python**: Follow PEP 8, use type hints
- **TypeScript**: Follow ESLint configuration
- **Comments**: Add docstrings for all classes and public methods
- **Testing**: Write tests for new features

### Pull Request Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution
- Additional language support
- New AI tool functions
- UI/UX improvements
- Performance optimizations
- Documentation improvements

---

## 🔒 Security

- API keys stored in environment variables (never committed)
- Google OAuth 2.0 for calendar access
- Twilio webhook signature verification
- Database credentials encrypted at rest
- CORS properly configured
- Rate limiting on API endpoints

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini and function calling capabilities
- **Twilio** for reliable telephony infrastructure
- **shadcn/ui** for beautiful UI components
- **Render** for seamless deployment platform

---

## 📞 Support & Contact

For questions, issues, or feature requests:
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-outbound-scheduler/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-outbound-scheduler/discussions)

---

<p align="center">
  <b>Built with ❤️ for modern AI-powered sales automation</b>
</p>

<p align="center">
  Made with FastAPI, React, OpenAI GPT-4o-mini, and Twilio
</p>
