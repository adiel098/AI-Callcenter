# Setup Guide - AI Outbound Meeting Scheduler

This guide will walk you through setting up the complete system from scratch.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

### Required Accounts & API Keys
- [ ] Twilio account with phone number
- [ ] OpenAI API key (for GPT-4o-mini)
- [ ] ElevenLabs API key
- [ ] Deepgram API key
- [ ] Google Cloud account with Calendar API enabled
- [ ] PostgreSQL database (local or Render)
- [ ] Redis instance (local or Upstash)

### Development Tools
- [ ] Python 3.11 or higher
- [ ] Node.js 18 or higher
- [ ] Git
- [ ] Code editor (VS Code recommended)

## 🚀 Step-by-Step Setup

### 1. Get API Keys

#### Twilio
1. Go to [twilio.com](https://www.twilio.com/) and sign up
2. Get a phone number
3. Copy Account SID and Auth Token from console
4. Fund account ($20 minimum for calls)

#### OpenAI
1. Go to [platform.openai.com](https://platform.openai.com/)
2. Create API key in settings
3. Add billing method

#### ElevenLabs
1. Go to [elevenlabs.io](https://elevenlabs.io/)
2. Sign up for free tier
3. Get API key from profile

#### Deepgram
1. Go to [deepgram.com](https://deepgram.com/)
2. Sign up for free tier ($200 credit)
3. Create API key

#### Google Calendar
1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials as `credentials.json`

### 2. Backend Setup

```bash
# Navigate to project
cd c:\Users\A\Desktop\HomeWork

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux

# Edit .env file with your API keys
notepad .env  # Windows
# nano .env  # Mac/Linux
```

#### Configure .env

Open `.env` and fill in all values:

```env
# Database (use local PostgreSQL or create on Render)
DATABASE_URL=postgresql://localhost:5432/ai_scheduler

# Redis (use local or Upstash free tier)
REDIS_URL=redis://localhost:6379/0

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# ElevenLabs
ELEVENLABS_API_KEY=your_key

# Deepgram
DEEPGRAM_API_KEY=your_key

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=your_email@gmail.com

# URLs (keep as localhost for development)
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Secret (generate random string)
SECRET_KEY=your-secret-key-change-this
```

#### Place Google Calendar Credentials

Copy your downloaded `credentials.json` to the project root:
```bash
copy Downloads\credentials.json c:\Users\A\Desktop\HomeWork\backend\credentials.json
```

### 3. Database Setup

#### Option A: Local PostgreSQL

```bash
# Install PostgreSQL if not installed
# Download from: https://www.postgresql.org/download/

# Create database
psql -U postgres
CREATE DATABASE ai_scheduler;
CREATE USER ai_scheduler_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_scheduler TO ai_scheduler_user;
\q
```

Update .env:
```env
DATABASE_URL=postgresql://ai_scheduler_user:your_password@localhost:5432/ai_scheduler
```

#### Option B: Render PostgreSQL (Recommended for production)

1. Create free PostgreSQL on [Render](https://render.com)
2. Copy internal connection string
3. Paste into .env as DATABASE_URL

### 4. Redis Setup

#### Option A: Local Redis

```bash
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Install and run Redis

# Mac:
brew install redis
brew services start redis

# Linux:
sudo apt-get install redis-server
sudo systemctl start redis
```

#### Option B: Upstash Redis (Recommended)

1. Go to [upstash.com](https://upstash.com/)
2. Create free Redis database
3. Copy connection string
4. Paste into .env as REDIS_URL

### 5. Initialize Database

```bash
cd backend
python -c "from database import init_db; init_db()"
```

You should see "Database initialized" message.

### 6. Test Backend

```bash
# Terminal 1: Start API
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start Celery worker (in new terminal)
cd backend
celery -A workers.celery_app worker --loglevel=info
```

Visit http://localhost:8000/docs to see API documentation.

### 7. Frontend Setup

```bash
# New terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit http://localhost:5173 to see dashboard.

## 🧪 Testing the System

### 1. Create Test Lead

```bash
curl -X POST http://localhost:8000/api/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "phone": "+12125551234",
    "email": "test@example.com"
  }'
```

### 2. Check Lead Created

Visit http://localhost:8000/api/leads/ or check the dashboard.

### 3. Start Test Campaign (without actual calling)

For testing without making real calls, you can:
1. Add test leads
2. Check database records
3. Test API endpoints

**Note**: To make actual calls, ensure Twilio account is funded and webhooks are configured.

## 🌐 Twilio Webhook Configuration

For calls to work, Twilio needs to reach your server:

### Development (using ngrok)

```bash
# Install ngrok from ngrok.com
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

In Twilio Console:
1. Go to Phone Numbers → Your Number
2. Set Voice webhook to: `https://abc123.ngrok.io/api/webhooks/twilio/voice`
3. Set Status callback to: `https://abc123.ngrok.io/api/webhooks/twilio/status`

### Production (Render)

When deployed, use your Render URL:
- Voice webhook: `https://ai-scheduler-api.onrender.com/api/webhooks/twilio/voice`
- Status callback: `https://ai-scheduler-api.onrender.com/api/webhooks/twilio/status`

## 📦 Deploying to Render

### 1. Prepare Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Create Render Services

1. Sign up at [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create:
   - Web Service (API)
   - Background Worker (Celery)
   - Static Site (Frontend)
   - PostgreSQL Database

### 3. Add Environment Variables

In each service settings, add all environment variables from your `.env` file.

**Important**: Use production URLs:
```env
API_BASE_URL=https://ai-scheduler-api.onrender.com
FRONTEND_URL=https://ai-scheduler-frontend.onrender.com
```

### 4. Add Redis

1. In Render, create a Redis instance OR
2. Use Upstash and add REDIS_URL to environment variables

### 5. Deploy

- Push to GitHub to trigger auto-deploy
- Monitor deployment logs in Render dashboard
- Services will be live in 5-10 minutes

## ✅ Verification Checklist

After setup, verify:

- [ ] Backend API is running (http://localhost:8000/health returns "healthy")
- [ ] Frontend loads (http://localhost:5173)
- [ ] Celery worker is running (check terminal for "celery@..." message)
- [ ] Database connection works (create a test lead)
- [ ] Redis connection works (worker receives tasks)
- [ ] API documentation is accessible (http://localhost:8000/docs)

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (should be 3.11+)
- Check all environment variables are set in .env
- Check database is running and accessible

### Celery worker won't start
- Check Redis is running: `redis-cli ping` (should return "PONG")
- Check REDIS_URL in .env is correct
- Try flushing Redis: `redis-cli FLUSHALL`

### Frontend won't start
- Check Node version: `node --version` (should be 18+)
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`
- Check VITE_API_URL is set correctly

### Calls not working
- Check Twilio credentials in .env
- Check account balance in Twilio console
- Check webhook URLs are set correctly
- Check ngrok is running (for local development)

### Database connection error
- Check PostgreSQL is running
- Check DATABASE_URL format is correct
- Check user has permissions

## 📚 Next Steps

After setup is complete:

1. **Add Real Leads**: Upload CSV with real contact information
2. **Test Calls**: Make test calls to your own number first
3. **Customize Prompts**: Edit system prompts in `backend/prompts/`
4. **Configure Calendar**: Set up proper Google Calendar integration
5. **Monitor**: Check dashboard for real-time metrics
6. **Scale**: Deploy to Render for production use

## 🎯 Production Checklist

Before going live:

- [ ] Use production database (not local)
- [ ] Set up proper monitoring (Sentry)
- [ ] Configure rate limiting
- [ ] Set up backup strategies
- [ ] Test with small batch first
- [ ] Verify call recording compliance
- [ ] Set up logging aggregation
- [ ] Configure auto-scaling rules

## 💡 Tips

- Start with a small test batch (5-10 leads)
- Monitor first few calls carefully
- Adjust system prompts based on results
- Use ngrok for local Twilio webhook testing
- Check Twilio logs for debugging
- Keep API keys secure (never commit to git)

## 📞 Support

If you encounter issues:
1. Check logs: Backend logs show errors
2. Review Twilio debugger: console.twilio.com/monitor/debugger
3. Check OpenAI usage: platform.openai.com/usage
4. Test individual components separately

---

**Ready to revolutionize outbound calling with AI! 🚀**
