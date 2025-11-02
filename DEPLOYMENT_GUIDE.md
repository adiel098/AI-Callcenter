# Complete Deployment Guide - AI Outbound Meeting Scheduler

This guide will walk you through deploying your AI call center to production on Render.

---

## Prerequisites

Before deploying, ensure you have:
- ✅ GitHub account with your code pushed
- ✅ Render account (sign up at https://render.com)
- ✅ All API keys ready:
  - Twilio (phone calls)
  - OpenAI (AI conversations)
  - ElevenLabs (text-to-speech)
  - Deepgram (speech-to-text)
  - Google Calendar service account

---

## Step 1: Set Up Render Account

1. Go to https://dashboard.render.com
2. Sign in with GitHub
3. Authorize Render to access your repositories

---

## Step 2: Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `ai-scheduler-db`
   - **Database**: `ai_scheduler`
   - **User**: `ai_scheduler_user`
   - **Region**: `Oregon (US West)`
   - **Plan**: `Free` (or `Starter` for production)
3. Click **"Create Database"**
4. Wait for provisioning (~2 minutes)
5. Copy the **Internal Database URL** (starts with `postgresql://`)
   - Format: `postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname`

---

## Step 3: Create Redis Instance

1. In Render Dashboard, click **"New +"** → **"Redis"**
2. Configure:
   - **Name**: `ai-scheduler-redis`
   - **Region**: `Oregon (US West)`
   - **Plan**: `Free` (or `Starter` for production)
   - **Maxmemory Policy**: `allkeys-lru`
3. Click **"Create Redis"**
4. Copy the **Redis Connection String**
   - Format: `redis://red-xxx.oregon-redis.render.com:6379`

---

## Step 4: Deploy Backend API (FastAPI)

### 4.1 Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-scheduler-api`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Starter` ($7/month) or `Free` (spins down after inactivity)

### 4.2 Add Environment Variables

Click **"Environment"** and add these variables:

```bash
# Python Version
PYTHON_VERSION=3.13.0

# Database (use Internal URL from Step 2)
DATABASE_URL=postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/ai_scheduler

# Redis (from Step 3)
REDIS_URL=redis://red-xxx.oregon-redis.render.com:6379

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxx

# ElevenLabs
ELEVENLABS_API_KEY=sk_xxxxxxxxxx

# Deepgram
DEEPGRAM_API_KEY=xxxxxxxxxx

# Google Calendar
GOOGLE_CALENDAR_ID=your_email@gmail.com

# Application URLs (update after deployment)
API_BASE_URL=https://ai-scheduler-api.onrender.com
FRONTEND_URL=https://ai-scheduler-frontend.onrender.com

# Security
SECRET_KEY=<click "Generate" to create random key>

# Optional: Sentry (error monitoring)
SENTRY_DSN=your_sentry_dsn

# Call Settings
MAX_CONCURRENT_CALLS=50
CALL_TIMEOUT_SECONDS=300
MAX_CONVERSATION_TURNS=20
```

### 4.3 Add Google Service Account File

1. Go to **"Environment"** → **"Secret Files"**
2. Click **"Add Secret File"**
3. **Filename**: `credentials.json`
4. **Contents**: Copy contents of your `backend/service-account.json`
5. Click **"Save Changes"**

### 4.4 Set Health Check

1. Go to **"Settings"** → **"Health & Alerts"**
2. **Health Check Path**: `/health`
3. Click **"Save Changes"**

### 4.5 Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait for build (~5-10 minutes)
3. Check logs for any errors
4. Once deployed, copy your service URL: `https://ai-scheduler-api.onrender.com`

---

## Step 5: Deploy Celery Worker

### 5.1 Create Background Worker

1. Click **"New +"** → **"Background Worker"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-scheduler-worker`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && celery -A workers.celery_app worker --loglevel=info --concurrency=4`
   - **Plan**: `Starter` ($7/month)

### 5.2 Add Environment Variables

Add the **same environment variables** as the API (Steps 4.2), except:
- Skip `API_BASE_URL`
- Skip `FRONTEND_URL`

### 5.3 Add Service Account File

Same as Step 4.3 - add `credentials.json` secret file

### 5.4 Configure Auto-Scaling (Optional)

1. Go to **"Scaling"**
2. Set:
   - **Min Instances**: `1`
   - **Max Instances**: `10`
   - **CPU Threshold**: `70%`

### 5.5 Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Check logs to verify worker starts and connects to Redis
3. You should see:
   ```
   [tasks]
     . backend.workers.tasks.finalize_call
     . backend.workers.tasks.initiate_call
     . backend.workers.tasks.process_conversation_turn
   ```

---

## Step 6: Deploy Frontend (React)

### 6.1 Create Static Site

1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `ai-scheduler-frontend`
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

### 6.2 Add Environment Variable

```bash
VITE_API_URL=https://ai-scheduler-api.onrender.com
```

(Use the URL from Step 4.5)

### 6.3 Configure Redirects

1. Go to **"Redirects/Rewrites"**
2. Add rule:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`

### 6.4 Deploy

1. Click **"Create Static Site"**
2. Wait for build (~3-5 minutes)
3. Once deployed, you'll get: `https://ai-scheduler-frontend.onrender.com`

---

## Step 7: Update Cross-Service URLs

Now that all services are deployed, update the URLs:

### 7.1 Update API Environment Variables

Go to **ai-scheduler-api** → **Environment**:
```bash
FRONTEND_URL=https://ai-scheduler-frontend.onrender.com
```

### 7.2 Update Worker Environment Variables

Go to **ai-scheduler-worker** → **Environment**:
```bash
API_BASE_URL=https://ai-scheduler-api.onrender.com
```

### 7.3 Redeploy Services

- Redeploy API
- Redeploy Worker

---

## Step 8: Initialize Database

### Option A: Via API Endpoint

Make a POST request to create tables:
```bash
curl -X POST https://ai-scheduler-api.onrender.com/api/admin/init-db
```

### Option B: Via Render Shell

1. Go to **ai-scheduler-api** service
2. Click **"Shell"** tab
3. Run:
   ```bash
   cd backend
   python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

---

## Step 9: Configure Twilio Webhooks

1. Go to Twilio Console → **Phone Numbers**
2. Select your Twilio number
3. Under **Voice & Fax**, set:
   - **A Call Comes In**: `Webhook`
   - **URL**: `https://ai-scheduler-api.onrender.com/api/webhooks/twilio/voice`
   - **HTTP Method**: `POST`
4. Under **Status Callback**:
   - **URL**: `https://ai-scheduler-api.onrender.com/api/webhooks/twilio/status`
5. Click **"Save"**

---

## Step 10: Share Google Calendar

1. Open your `backend/service-account.json` (or `credentials.json` on Render)
2. Copy the `client_email`:
   ```
   callcenter@callcenter-477010.iam.gserviceaccount.com
   ```
3. Go to https://calendar.google.com
4. Select your calendar → **Settings and sharing**
5. Scroll to **"Share with specific people"**
6. Click **"Add people"**
7. Paste the service account email
8. Permission: **"Make changes to events"**
9. Click **"Send"**

---

## Step 11: Test Deployment

### 11.1 Access Frontend

Visit: `https://ai-scheduler-frontend.onrender.com`

You should see:
- Login page or Dashboard
- No console errors

### 11.2 Test API Health

Visit: `https://ai-scheduler-api.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

### 11.3 Test API Docs

Visit: `https://ai-scheduler-api.onrender.com/docs`

You should see FastAPI Swagger documentation

### 11.4 Check Worker Logs

1. Go to **ai-scheduler-worker** service
2. Click **"Logs"**
3. Verify no errors and worker is connected to Redis

### 11.5 Upload Test Lead

1. In the dashboard, go to **"Leads"**
2. Upload a CSV with:
   ```csv
   name,email,phone
   Test User,test@example.com,+1234567890
   ```
3. Create a campaign
4. Start the campaign
5. Check worker logs to see call being processed

---

## Step 12: Monitor and Maintain

### Set Up Monitoring

1. **Render Alerts**:
   - Go to each service → **Health & Alerts**
   - Enable email alerts for failures

2. **Sentry** (Optional but recommended):
   - Sign up at https://sentry.io
   - Create new project
   - Copy DSN and add to environment variables

### Check Logs Regularly

- **API Logs**: Check for failed requests
- **Worker Logs**: Monitor call processing
- **Database**: Check connection and performance metrics

### Scale as Needed

- **API**: Increase plan for more concurrent requests
- **Worker**: Increase instances for more concurrent calls
- **Database**: Upgrade plan for more connections

---

## Troubleshooting

### API Won't Start

- Check environment variables are set correctly
- Verify DATABASE_URL is valid
- Check build logs for dependency errors
- Ensure Python 3.13 is specified

### Worker Can't Connect to Redis

- Verify REDIS_URL is correct
- Check Redis instance is running
- Ensure Redis is in same region as worker

### Calls Not Being Made

- Verify Twilio credentials are correct
- Check Twilio phone number is verified
- Verify webhook URLs are configured
- Check worker logs for errors

### Calendar Not Working

- Verify service account email is shared with calendar
- Check GOOGLE_CALENDAR_ID matches your calendar
- Ensure credentials.json is uploaded correctly

### Database Connection Errors

- Verify DATABASE_URL format
- Check database instance is running
- Ensure SSL mode is included in connection string

---

## Cost Breakdown (Render Pricing)

### Free Tier (Development)
- Web Service: Free (spins down after 15 min inactivity)
- Database: Free (shared CPU, 1GB storage)
- Redis: Free (25MB)
- Static Site: Free
- **Total**: $0/month

### Production Tier (Recommended)
- Web Service (Starter): $7/month
- Worker (Starter): $7/month
- Database (Starter): $7/month
- Redis (Starter): $10/month
- Static Site: Free
- **Total**: $31/month

### Scale Tier (High Volume)
- Web Service (Standard): $25/month
- Worker (Standard, 2 instances): $50/month
- Database (Standard): $25/month
- Redis (Standard): $25/month
- Static Site: Free
- **Total**: $125/month

---

## Alternative Deployment Options

### AWS/GCP/Azure

If you prefer other cloud providers:

1. **API**: Deploy as Docker container or use Elastic Beanstalk/App Engine/App Service
2. **Worker**: Deploy as separate container or compute instance
3. **Database**: Use managed PostgreSQL (RDS/Cloud SQL/Azure Database)
4. **Redis**: Use managed Redis (ElastiCache/Memorystore/Azure Cache)
5. **Frontend**: Deploy to S3+CloudFront / Cloud Storage+CDN / Azure Static Web Apps

### Docker Compose (Self-Hosted)

See `docker-compose.yml` in repository for self-hosted deployment.

---

## Security Best Practices

1. **Environment Variables**: Never commit API keys to Git
2. **HTTPS Only**: Ensure all services use HTTPS
3. **Database**: Use strong passwords, enable SSL
4. **API Rate Limiting**: Configure rate limits in FastAPI
5. **CORS**: Only allow your frontend domain
6. **Twilio**: Validate webhook signatures
7. **Monitoring**: Set up alerts for unusual activity

---

## Next Steps

Once deployed:

1. ✅ Test end-to-end call flow
2. ✅ Monitor logs for first 24 hours
3. ✅ Set up backup strategy for database
4. ✅ Configure auto-scaling rules
5. ✅ Add custom domain (optional)
6. ✅ Set up CI/CD for automatic deployments
7. ✅ Create runbooks for common issues

---

## Support

- **Render Docs**: https://render.com/docs
- **Project Docs**: See CLAUDE.md, SETUP.md, README.md
- **Issues**: Check logs in Render dashboard
- **Community**: Render Discord / Stack Overflow

---

**Congratulations! Your AI Outbound Meeting Scheduler is now live! 🎉**
