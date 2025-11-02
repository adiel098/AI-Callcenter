# Deployment Checklist - What's Left to Run the Platform

## Current Status

✅ **Completed:**
- Project code structure
- Git repository initialized
- Pushed to GitHub
- `.gitignore` configured
- Service account created
- `.env` file exists

❌ **Remaining Tasks:**

---

## 1. Database Setup

### Option A: Local PostgreSQL (For Testing)
```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/

# Create database
psql -U postgres
CREATE DATABASE ai_scheduler;
CREATE USER ai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_scheduler TO ai_user;
\q

# Update .env
DATABASE_URL=postgresql://ai_user:your_password@localhost:5432/ai_scheduler
```

### Option B: Render PostgreSQL (Recommended)
```bash
# 1. Go to https://dashboard.render.com/
# 2. Click "New +" → "PostgreSQL"
# 3. Name: homework-db
# 4. Copy "Internal Database URL"
# 5. Update .env:
DATABASE_URL=postgresql://user:pass@dpg-xyz.oregon-postgres.render.com/homework
```

**Status:** ⏳ **You need to do this**

---

## 2. Redis Setup

### Option A: Local Redis (Docker - Easiest)
```bash
# Install Docker Desktop: https://www.docker.com/products/docker-desktop

# Run Redis
docker run -d -p 6379:6379 --name homework-redis redis:alpine

# Update .env
REDIS_URL=redis://localhost:6379/0
```

### Option B: Render Redis (Recommended for Production)
```bash
# 1. Go to https://dashboard.render.com/
# 2. Click "New +" → "Key Value" (this is Redis)
# 3. Name: homework-redis
# 4. Plan: Free
# 5. Copy connection URL
# 6. Update .env:
REDIS_URL=redis://red-xyz:6379
```

**Status:** ⏳ **You need to do this**

---

## 3. Google Calendar Setup

### Share Calendar with Service Account

**You have:** `backend/service-account.json` ✅

**Still need to do:**

1. Open `backend/service-account.json`
2. Copy the `client_email`:
   ```
   callcenter@callcenter-477010.iam.gserviceaccount.com
   ```

3. Go to https://calendar.google.com
4. Click your calendar → **Settings and sharing**
5. Scroll to **"Share with specific people"**
6. Click **"Add people"**
7. Paste: `callcenter@callcenter-477010.iam.gserviceaccount.com`
8. Permission: **"Make changes to events"**
9. Click **"Send"**

10. Update `.env`:
```env
GOOGLE_CALENDAR_ID=your_email@gmail.com
```

**Status:** ⏳ **You need to share calendar**

---

## 4. API Keys Configuration

Update your `.env` file with real API keys:

### Twilio (Phone Calls)
```bash
# Sign up: https://www.twilio.com/try-twilio
# Get free trial account

TWILIO_ACCOUNT_SID=ACxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### OpenAI (AI Conversations)
```bash
# Get API key: https://platform.openai.com/api-keys

OPENAI_API_KEY=sk-proj-xxxxxxxxx
```

### ElevenLabs (Text-to-Speech)
```bash
# Sign up: https://elevenlabs.io/
# Get free API key

ELEVENLABS_API_KEY=sk_xxxxxxxxx
```

### Deepgram (Speech-to-Text)
```bash
# Sign up: https://console.deepgram.com/
# Get free API key

DEEPGRAM_API_KEY=xxxxxxxxx
```

**Status:** ⏳ **You need to add real API keys to .env**

---

## 5. Install Dependencies

### Backend Dependencies
```bash
cd c:/Users/A/Desktop/HomeWork/backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd c:/Users/A/Desktop/HomeWork/frontend
npm install
```

**Status:** ⏳ **You need to install**

---

## 6. Database Migration

Create database tables:

```bash
cd c:/Users/A/Desktop/HomeWork
python -c "from backend.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

**Status:** ⏳ **Run after database is configured**

---

## 7. Test Components

### Test Database Connection
```bash
python backend/database.py
```

### Test Calendar Service
```python
from backend.services.calendar_service import CalendarService

calendar = CalendarService()
slots = calendar.get_next_available_slots(count=3)
print(slots)
```

### Test Redis Connection
```python
import redis
from backend.config import get_settings

settings = get_settings()
r = redis.from_url(settings.redis_url)
print(r.ping())  # Should return True
```

**Status:** ⏳ **Test after setup**

---

## 8. Start Services

### Start Backend API
```bash
cd c:/Users/A/Desktop/HomeWork
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Start Celery Worker (Separate Terminal)
```bash
cd c:/Users/A/Desktop/HomeWork
celery -A backend.workers.celery_app worker --loglevel=info
```

Should see:
```
[tasks]
  . backend.workers.tasks.initiate_call
  . backend.workers.tasks.process_conversation_turn
```

### Start Frontend (Separate Terminal)
```bash
cd c:/Users/A/Desktop/HomeWork/frontend
npm run dev
```

Should see:
```
VITE ready in XXX ms
Local: http://localhost:5173/
```

**Status:** ⏳ **Start after all setup is complete**

---

## 9. Access Dashboard

Open browser:
```
http://localhost:5173
```

You should see the AI Callcenter Dashboard with:
- Dashboard (KPIs)
- Leads management
- Calls history
- Meetings scheduled
- Analytics

**Status:** ⏳ **After services are running**

---

## 10. Test Complete Flow

1. **Upload leads** (CSV with: name, email, phone)
2. **Create campaign**
3. **Start campaign** → Celery worker picks up tasks
4. **System makes call** → Twilio
5. **AI conversation** → OpenAI + Deepgram + ElevenLabs
6. **Meeting booked** → Google Calendar
7. **View results** in dashboard

**Status:** ⏳ **Final test**

---

## Quick Start Summary

**Minimum to run locally:**

```bash
# 1. Set up services (choose one from each):
# - PostgreSQL: Local or Render
# - Redis: Docker or Render

# 2. Update .env with:
# - DATABASE_URL
# - REDIS_URL
# - All API keys
# - GOOGLE_CALENDAR_ID=your_email@gmail.com

# 3. Share calendar with service account

# 4. Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install

# 5. Create database tables
python -c "from backend.database import Base, engine; Base.metadata.create_all(bind=engine)"

# 6. Start services (3 terminals):

# Terminal 1: API
uvicorn backend.main:app --reload

# Terminal 2: Celery Worker
celery -A backend.workers.celery_app worker --loglevel=info

# Terminal 3: Frontend
cd frontend && npm run dev

# 7. Open browser
# http://localhost:5173
```

---

## Production Deployment (Render)

When ready for production:

1. **Connect GitHub repo** to Render
2. **Add environment variables** in Render dashboard
3. **Upload service-account.json** as secret file
4. **Deploy** - Render auto-builds from `render.yaml`

See [SETUP.md](SETUP.md) for detailed production deployment guide.

---

## Checklist Progress

Track your progress:

- [ ] PostgreSQL database created
- [ ] Redis running
- [ ] Google Calendar shared with service account
- [ ] All API keys added to `.env`
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database tables created
- [ ] Backend API running
- [ ] Celery worker running
- [ ] Frontend running
- [ ] Dashboard accessible
- [ ] Test call completed

---

## Need Help?

- **Database issues**: Check connection string format
- **Redis issues**: Ensure port 6379 is not blocked
- **Calendar issues**: Verify service account has access
- **API issues**: Check all API keys are valid
- **Dependency issues**: Use Python 3.9+ and Node 16+

**Check logs in each terminal for error messages!**
