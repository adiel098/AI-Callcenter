# Google Calendar Setup Guide

This guide covers setting up Google Calendar for **both development and production** environments.

---

## Authentication Methods

| Method | Use Case | Browser Required | File Needed |
|--------|----------|------------------|-------------|
| **OAuth** | Development/Testing | ✅ Yes | `credentials.json` + `token.json` |
| **Service Account** | Production/Server | ❌ No | `service-account.json` |

---

## Method 1: OAuth (Development)

Use this when developing locally on your machine.

### Step 1: Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `callcenter-477010`
3. Enable **Google Calendar API**:
   - Go to [API Library](https://console.cloud.google.com/apis/library)
   - Search: "Google Calendar API"
   - Click **Enable**

4. Create **OAuth 2.0 Client ID**:
   - Go to [Credentials](https://console.cloud.google.com/apis/credentials)
   - Click **"Create Credentials"** → **"OAuth client ID"**
   - **Application type**: **Desktop app** ⚠️ (NOT Web application)
   - **Name**: `HomeWork Desktop Client`
   - Click **"Create"**

5. **Download credentials**:
   - Click the **Download** button (⬇️)
   - Save as: `c:\Users\A\Desktop\HomeWork\backend\credentials.json`

### Step 2: Generate Token

```bash
cd c:\Users\A\Desktop\HomeWork
python backend\utils\setup_calendar.py
```

This will:
- ✅ Open your browser
- ✅ Ask you to log in to Google
- ✅ Request calendar permissions
- ✅ Generate `backend/token.json`

### Step 3: Update `.env`

```env
GOOGLE_CALENDAR_CREDENTIALS_FILE=backend/credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=backend/token.json
GOOGLE_CALENDAR_ID=your_email@gmail.com
```

---

## Method 2: Service Account (Production)

Use this for servers/production where no browser is available.

### Step 1: Create Service Account

1. Go to [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click **"Create Service Account"**
3. Configure:
   - **Name**: `homework-calendar-bot`
   - **Description**: `AI calling system calendar access`
   - Click **"Create and Continue"**
   - **Skip** role assignment (click "Continue")
   - Click **"Done"**

### Step 2: Create Key

1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **JSON** format
5. Click **"Create"**
6. Save as: `c:\Users\A\Desktop\HomeWork\backend\service-account.json`

### Step 3: Share Calendar with Service Account

⚠️ **IMPORTANT**: The service account needs access to your calendar!

1. Open the downloaded `service-account.json`
2. Copy the **`client_email`** value (looks like):
   ```
   homework-calendar-bot@callcenter-477010.iam.gserviceaccount.com
   ```

3. Go to [Google Calendar](https://calendar.google.com)
4. **Option A: Share existing calendar**:
   - Click on your calendar → **Settings and sharing**
   - Scroll to **"Share with specific people"**
   - Click **"Add people"**
   - Paste the service account email
   - Set permissions: **"Make changes to events"**
   - Click **"Send"**

5. **Option B: Create dedicated calendar** (Recommended):
   - Create new calendar: **"AI Calling Meetings"**
   - Share it with the service account email (steps above)
   - Use this calendar ID in `.env`

### Step 4: Update `.env`

```env
# Service account takes priority over OAuth
GOOGLE_CALENDAR_ID=your_email@gmail.com
# OR if you created a dedicated calendar:
# GOOGLE_CALENDAR_ID=abc123@group.calendar.google.com
```

---

## How It Works

The `CalendarService` automatically detects which method to use:

```
1. Check if backend/service-account.json exists
   ✅ YES → Use Service Account (Production mode)
   ❌ NO → Use OAuth (Development mode)

2. OAuth fallback:
   - Check if backend/token.json exists
   - If valid → Use it
   - If expired → Refresh it
   - If missing → Run OAuth flow
```

---

## Testing

### Test Service Account

```python
from backend.services.calendar_service import CalendarService

# This will use service-account.json if it exists
calendar = CalendarService()

# Get available slots
slots = calendar.get_next_available_slots(count=3)
print(slots)

# Create test meeting
from datetime import datetime, timedelta
start = datetime.utcnow() + timedelta(days=1)
end = start + timedelta(minutes=30)

meeting_id = calendar.create_meeting(
    summary="Test Meeting",
    start_time=start,
    end_time=end,
    attendee_email="test@example.com",
    description="Testing service account"
)
print(f"Meeting created: {meeting_id}")
```

---

## Deployment Checklist

### For Render Deployment

1. ✅ Create service account
2. ✅ Download `service-account.json`
3. ✅ Share calendar with service account email
4. ✅ Add to Render:
   - Go to Render dashboard
   - Select your web service
   - Go to **"Environment"** tab
   - Add **Secret File**:
     - **Filename**: `backend/service-account.json`
     - **Contents**: Paste entire JSON content
   - Click **"Save Changes"**

5. ✅ Update environment variables:
   ```env
   GOOGLE_CALENDAR_ID=your_email@gmail.com
   ```

---

## Troubleshooting

### Error: "redirect_uri_mismatch"
- ❌ You created **Web application** credentials
- ✅ Delete and recreate as **Desktop app**

### Error: "Access Not Granted"
- ❌ Service account doesn't have calendar access
- ✅ Share calendar with service account email

### Error: "Calendar not found"
- ❌ Wrong calendar ID in `.env`
- ✅ Use your primary email or dedicated calendar ID

### Error: "Invalid credentials"
- ❌ Wrong JSON file or corrupted
- ✅ Re-download from Google Cloud Console

---

## Security Notes

⚠️ **NEVER commit these files to git**:
- `credentials.json` (OAuth secret)
- `token.json` (OAuth token)
- `service-account.json` (Service account key)

Add to `.gitignore`:
```gitignore
backend/credentials.json
backend/token.json
backend/service-account.json
```

---

## Summary

**Development** (Local):
```
1. Create OAuth credentials (Desktop app)
2. Download credentials.json
3. Run setup_calendar.py
4. Get token.json
5. Done!
```

**Production** (Render):
```
1. Create service account
2. Download service-account.json
3. Share calendar with service account email
4. Upload to Render as secret file
5. Done!
```

The system automatically uses the right method based on which files exist!
