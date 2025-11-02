# Local Development Setup Guide

This guide will help you run the AI Outbound Meeting Scheduler locally on your machine for testing and development.

---

## Prerequisites

Before starting, ensure you have:
- ✅ Python 3.13 installed
- ✅ Node.js 16+ and npm installed
- ✅ Git installed

---

## Step 1: Install Docker Desktop (for Redis)

Redis is needed for Celery task queue. The easiest way to run Redis locally is with Docker.

### Windows:
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   ```

### Alternative (Without Docker):
If you can't use Docker, you can use a cloud Redis for free:
1. Sign up at https://upstash.com (free tier)
2. Create a Redis database
3. Copy the connection URL

---

## Step 2: Set Up PostgreSQL Database

### Option A: Use Docker (Recommended)

```bash
# Start PostgreSQL in Docker
docker run -d \
  --name homework-postgres \
  -e POSTGRES_USER=ai_user \
  -e POSTGRES_PASSWORD=ai_password \
  -e POSTGRES_DB=ai_scheduler \
  -p 5432:5432 \
  postgres:15-alpine

# Verify it's running
docker ps
```

Your DATABASE_URL will be:
```
DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_scheduler
```

### Option B: Install PostgreSQL Locally

1. Download from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for the `postgres` user
4. Open pgAdmin or psql and create database:
   ```sql
   CREATE DATABASE ai_scheduler;
   CREATE USER ai_user WITH PASSWORD 'ai_password';
   GRANT ALL PRIVILEGES ON DATABASE ai_scheduler TO ai_user;
   ```

### Option C: Use Cloud PostgreSQL (Free)

1. Sign up at https://render.com or https://supabase.com
2. Create a PostgreSQL database (free tier)
3. Copy the connection URL

---

## Step 3: Set Up Redis

### Using Docker (Recommended):

```bash
# Start Redis in Docker
docker run -d \
  --name homework-redis \
  -p 6379:6379 \
  redis:alpine

# Verify it's running
docker exec -it homework-redis redis-cli ping
# Should return: PONG
```

Your REDIS_URL will be:
```
REDIS_URL=redis://localhost:6379/0
```

### Using Cloud Redis (Free Alternative):

1. Go to https://upstash.com
2. Sign up (free)
3. Create Redis database
4. Copy connection URL (format: `redis://default:password@host:port`)

---

## Step 4: Get API Keys

You'll need these API keys. Most have free tiers for testing:

### 1. Twilio (Phone Calls)
```bash
# Sign up: https://www.twilio.com/try-twilio
# After signup, you'll get:
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1234567890  # Trial number provided
```

**Free Trial**: $15 credit, can make test calls

### 2. OpenAI (AI Conversations)
```bash
# Sign up: https://platform.openai.com/signup
# Go to: https://platform.openai.com/api-keys
# Click "Create new secret key"
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx
```

**Pricing**: Pay as you go (~$0.01 per call)

### 3. ElevenLabs (Text-to-Speech)
```bash
# Sign up: https://elevenlabs.io/sign-up
# Go to Profile → API Keys
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxx
```

**Free Tier**: 10,000 characters/month

### 4. Deepgram (Speech-to-Text)
```bash
# Sign up: https://console.deepgram.com/signup
# Go to API Keys → Create Key
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxx
```

**Free Tier**: $200 credit

### 5. Google Calendar (Meeting Booking)

You already have `backend/service-account.json`. Now:

1. Go to https://calendar.google.com
2. Settings → **Share with specific people**
3. Add: `callcenter@callcenter-477010.iam.gserviceaccount.com`
4. Permission: **Make changes to events**
5. Your calendar ID is your email: `your_email@gmail.com`

---

## Step 5: Configure Environment Variables

1. Copy the example env file:
   ```bash
   cd c:\Users\A\Desktop\HomeWork
   copy .env.example .env
   ```

2. Edit `.env` with your actual values:
   ```bash
   notepad .env
   ```

3. Update these values:

```env
# Database (from Step 2)
DATABASE_URL=postgresql://ai_user:ai_password@localhost:5432/ai_scheduler

# Redis (from Step 3)
REDIS_URL=redis://localhost:6379/0

# Twilio (from Step 4)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+15551234567

# OpenAI (from Step 4)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx

# ElevenLabs (from Step 4)
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxx

# Deepgram (from Step 4)
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxx

# Google Calendar (from Step 4)
GOOGLE_CALENDAR_CREDENTIALS_FILE=backend/service-account.json
GOOGLE_CALENDAR_ID=your_email@gmail.com

# Application URLs (local)
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Security (generate random string)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Optional: Sentry (leave empty for now)
SENTRY_DSN=

# Call Settings
MAX_CONCURRENT_CALLS=5
CALL_TIMEOUT_SECONDS=300
MAX_CONVERSATION_TURNS=20
```

---

## Step 6: Install Dependencies

### Backend Dependencies:

```bash
cd c:\Users\A\Desktop\HomeWork

# Install with Python 3.13
py -3.13 -m pip install -r backend/requirements.txt
```

Expected output:
```
Successfully installed fastapi uvicorn sqlalchemy celery redis twilio openai elevenlabs deepgram-sdk...
```

### Frontend Dependencies:

```bash
cd c:\Users\A\Desktop\HomeWork\frontend

npm install
```

Expected output:
```
added XXX packages in XXs
```

---

## Step 7: Initialize Database

Create the database tables:

```bash
cd c:\Users\A\Desktop\HomeWork

py -3.13 -c "from backend.database import Base, engine; Base.metadata.create_all(bind=engine); print('✅ Database tables created!')"
```

Expected output:
```
✅ Database tables created!
```

---

## Step 8: Test Services

### Test Database Connection:

```bash
py -3.13 -c "from backend.database import engine; conn = engine.connect(); print('✅ Database connected!'); conn.close()"
```

### Test Redis Connection:

```bash
py -3.13 -c "import redis; from backend.config import get_settings; r = redis.from_url(get_settings().redis_url); print('✅ Redis connected!' if r.ping() else '❌ Redis failed')"
```

### Test Google Calendar:

```bash
py -3.13 -c "from backend.services.calendar_service import CalendarService; cal = CalendarService(); slots = cal.get_next_available_slots(3); print(f'✅ Calendar working! Found {len(slots)} slots')"
```

---

## Step 9: Start All Services

You'll need **3 terminal windows**:

### Terminal 1: Start Backend API

```bash
cd c:\Users\A\Desktop\HomeWork
py -3.13 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test it**: Open browser to http://localhost:8000/docs

### Terminal 2: Start Celery Worker

```bash
cd c:\Users\A\Desktop\HomeWork
py -3.13 -m celery -A backend.workers.celery_app worker --loglevel=info --pool=solo
```

Expected output:
```
[tasks]
  . backend.workers.tasks.finalize_call
  . backend.workers.tasks.initiate_call
  . backend.workers.tasks.process_conversation_turn

celery@DESKTOP ready.
```

**Note**: Use `--pool=solo` on Windows. This is already correct in your command.

### Terminal 3: Start Frontend

```bash
cd c:\Users\A\Desktop\HomeWork\frontend
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

---

## Step 10: Access the Dashboard

Open your browser to: **http://localhost:5173**

You should see:
- Dashboard with KPIs
- Leads management page
- Calls history
- Meetings calendar
- Analytics

---

## Step 11: Test Complete Flow

### 1. Create a Test Lead (CSV):

Create `test_leads.csv`:
```csv
name,email,phone
John Doe,john@example.com,+1234567890
Jane Smith,jane@example.com,+1987654321
```

### 2. Upload Leads:

1. Go to **Leads** page
2. Click **"Upload CSV"**
3. Select `test_leads.csv`
4. Leads should appear in the table

### 3. Create Campaign:

1. Go to **Campaigns** page
2. Click **"Create Campaign"**
3. Name: "Test Campaign"
4. Select leads
5. Click **"Start Campaign"**

### 4. Watch Worker Process:

In Terminal 2 (Celery worker), you should see:
```
[INFO] [TOOLS] Initiating call to John Doe (+1234567890) with function calling enabled
[INFO] [TOOLS] Call initiated: CA12345...
```

### 5. Check Results:

- Go to **Calls** page to see call logs
- Go to **Meetings** page to see booked meetings
- Check your Google Calendar for scheduled meetings

---

## Troubleshooting

### ❌ "Cannot connect to database"

**Fix**:
- Verify PostgreSQL is running: `docker ps` (if using Docker)
- Check DATABASE_URL in `.env` is correct
- Test connection: `py -3.13 -c "from backend.database import engine; engine.connect()"`

### ❌ "Cannot connect to Redis"

**Fix**:
- Verify Redis is running: `docker ps` (if using Docker)
- Check REDIS_URL in `.env` is correct
- Test: `docker exec -it homework-redis redis-cli ping`

### ❌ "Calendar service not working"

**Fix**:
- Verify you shared calendar with service account email
- Check `backend/service-account.json` exists
- Verify GOOGLE_CALENDAR_ID in `.env` is your email

### ❌ "Module not found" errors

**Fix**:
```bash
# Ensure you're using Python 3.13
py -3.13 -m pip install -r backend/requirements.txt

# If still failing, try:
py -3.13 -m pip install --upgrade pip
py -3.13 -m pip install -r backend/requirements.txt --force-reinstall
```

### ❌ Celery worker won't start

**Fix**:
```bash
# On Windows, always use --pool=solo
py -3.13 -m celery -A backend.workers.celery_app worker --loglevel=info --pool=solo

# If still failing, check Redis connection
py -3.13 -c "import redis; from backend.config import get_settings; r = redis.from_url(get_settings().redis_url); print(r.ping())"
```

### ❌ Frontend won't build

**Fix**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### ❌ Port already in use

**Fix**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use different ports:
# Backend: --port 8001
# Frontend: npm run dev -- --port 5174
```

---

## Quick Start Commands

After initial setup, use these commands to start development:

```bash
# Start Docker services (if using Docker)
docker start homework-postgres homework-redis

# Terminal 1: API
cd c:\Users\A\Desktop\HomeWork
py -3.13 -m uvicorn backend.main:app --reload

# Terminal 2: Worker
cd c:\Users\A\Desktop\HomeWork
py -3.13 -m celery -A backend.workers.celery_app worker --loglevel=info --pool=solo

# Terminal 3: Frontend
cd c:\Users\A\Desktop\HomeWork\frontend
npm run dev
```

---

## Development Tips

### Hot Reload

All services support hot reload:
- **Backend**: Code changes auto-reload (uvicorn `--reload`)
- **Frontend**: Changes show instantly (Vite HMR)
- **Worker**: Restart manually when changing worker code (`Ctrl+C` then restart)

### View Logs

- **API Logs**: Terminal 1
- **Worker Logs**: Terminal 2
- **Browser Console**: F12 in browser
- **Database Queries**: Add `echo=True` in `backend/database.py`

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Database Management

View database:
```bash
# If using Docker
docker exec -it homework-postgres psql -U ai_user -d ai_scheduler

# Commands:
\dt                    # List tables
SELECT * FROM leads;   # View leads
SELECT * FROM calls;   # View calls
\q                     # Quit
```

### Clear Data

To reset database:
```bash
py -3.13 -c "from backend.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); print('✅ Database reset!')"
```

---

## Testing Without Making Real Calls

If you don't have Twilio or want to test without making real calls:

### 1. Mock Mode (Recommended for Testing)

Add to `.env`:
```env
MOCK_CALLS=true
```

This will:
- Simulate call flow without Twilio
- Generate fake transcripts
- Test AI conversation logic
- Book test meetings

### 2. Test with Ngrok (Real Calls Locally)

To test real Twilio calls locally:

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update Twilio webhook URLs to:
# https://abc123.ngrok.io/api/webhooks/twilio/voice
# https://abc123.ngrok.io/api/webhooks/twilio/status
```

---

## Environment Checklist

Before starting development, verify:

- [ ] Docker Desktop running (if using Docker)
- [ ] PostgreSQL running and accessible
- [ ] Redis running and accessible
- [ ] `.env` file configured with all keys
- [ ] Google Calendar shared with service account
- [ ] All dependencies installed (Python + Node)
- [ ] Database tables created
- [ ] Port 8000, 6379, 5432, 5173 available

---

## Next Steps

Once everything is working locally:

1. ✅ Test uploading leads
2. ✅ Test creating campaigns
3. ✅ Test call flow (with mock or real calls)
4. ✅ Verify meetings appear in Google Calendar
5. ✅ Check all dashboard pages work
6. ✅ When satisfied, follow DEPLOYMENT_GUIDE.md to deploy to production

---

## Getting Help

**Check logs in all 3 terminals for error messages!**

Common issues:
- Missing API keys → Check `.env` file
- Connection errors → Verify services are running
- Import errors → Reinstall dependencies with Python 3.13
- Port conflicts → Use different ports or kill processes

**Need more help?** Check:
- [CLAUDE.md](CLAUDE.md) - Project architecture
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Setup checklist
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment

---

**Happy coding! 🚀**
