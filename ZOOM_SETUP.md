# Zoom Integration Setup Guide

**Simple alternative to Google Meet - No delegation or Google Workspace required!**

This guide explains how to add Zoom meeting links to your calendar events.

## Why Zoom?

✅ **Simpler** than Google Meet (no Domain-Wide Delegation needed)
✅ **Works with free Zoom accounts**
✅ **No Google Workspace required**
✅ **5-minute setup**

---

## Step 1: Create Zoom Server-to-Server OAuth App (5 minutes)

1. Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click **"Develop"** → **"Build App"**
3. Select **"Server-to-Server OAuth"**
4. Fill in app information:
   - **App Name:** AI Call Center
   - **Company Name:** Your Company
   - **Developer Contact:** your@email.com
5. Click **"Create"**

---

## Step 2: Get Your Credentials

After creating the app, you'll see:

1. **Account ID** - Copy this
2. **Client ID** - Copy this
3. **Client Secret** - Copy this

---

## Step 3: Add Scopes

In your app settings:

1. Go to **"Scopes"** tab
2. Click **"Add Scopes"**
3. Add these scopes:
   - `meeting:write` (Create meetings)
   - `meeting:write:admin` (Admin create meetings)
4. Click **"Done"**
5. **Important:** Click **"Continue"** to activate the app

---

## Step 4: Update .env File

Add these three lines to your `.env` file:

```bash
ZOOM_ACCOUNT_ID=your_account_id_here
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
```

---

## Step 5: Test It Works

Create a test script:

```python
from backend.services.zoom_service import ZoomService
from datetime import datetime, timedelta

zoom = ZoomService()

# Create a test meeting
meeting = zoom.create_meeting(
    topic="Test Meeting",
    start_time=datetime.utcnow() + timedelta(hours=1),
    duration=30,
    agenda="Testing Zoom integration"
)

if meeting:
    print(f"✅ SUCCESS!")
    print(f"Join URL: {meeting['join_url']}")
    print(f"Meeting ID: {meeting['meeting_id']}")
    print(f"Password: {meeting['password']}")
else:
    print("❌ FAILED - Check your credentials")
```

---

## How It Works

1. User books a meeting through your AI call center
2. System creates calendar event (Google Calendar)
3. System creates Zoom meeting link (Zoom API)
4. Both are saved to database
5. User receives calendar invite with Zoom link

---

## Integration with Calendar Service

The Zoom link can be added to calendar descriptions:

```python
# In your booking code
zoom_service = ZoomService()
zoom_meeting = zoom_service.create_meeting(
    topic=meeting_title,
    start_time=meeting_datetime,
    duration=duration_minutes,
    agenda=description
)

if zoom_meeting:
    # Add Zoom link to calendar description
    calendar_description = f"{description}\n\nJoin Zoom Meeting:\n{zoom_meeting['join_url']}"

    # Create calendar event with Zoom link in description
    calendar_service.create_meeting(
        summary=meeting_title,
        start_time=meeting_datetime,
        end_time=end_time,
        attendee_email=guest_email,
        description=calendar_description
    )
```

---

## Pricing

**Zoom API is FREE for:**
- Up to 100 meeting participants (free account)
- Unlimited meetings
- No additional API costs

**Note:** Your regular Zoom account limits still apply (40-minute limit on free accounts for 3+ participants).

---

## Advantages Over Google Meet

| Feature | Zoom API | Google Meet API |
|---------|----------|-----------------|
| Setup Time | 5 minutes | 30+ minutes |
| Requirements | Free Zoom account | Google Workspace + Admin |
| Delegation | Not needed | Domain-Wide Delegation |
| Cost | Free | Requires Google Workspace |
| Complexity | Simple | Complex |

---

## Troubleshooting

### Error: "Invalid access token"
**Cause:** Credentials are wrong or app not activated
**Fix:**
1. Double-check Account ID, Client ID, Client Secret
2. Make sure you clicked "Continue" to activate the app
3. Verify scopes are added

### Error: "User does not exist"
**Cause:** App not properly activated
**Fix:**
1. Go to your app in Zoom Marketplace
2. Click "Activation" tab
3. Make sure status is "Activated"

### No meeting created
**Cause:** Missing API scopes
**Fix:**
1. Add both `meeting:write` and `meeting:write:admin` scopes
2. Click "Continue" to save
3. Try again

---

## Security Considerations

- ⚠️ Store credentials in `.env` file (never commit to git)
- ⚠️ Credentials in `.env` are already gitignored
- ⚠️ Use Server-to-Server OAuth (not JWT - being deprecated)
- ✅ Zoom credentials are separate from your Zoom login password

---

## Next Steps

1. Create Zoom app (5 min)
2. Add credentials to `.env`
3. Restart backend
4. Test meeting creation
5. Enjoy simple video conferencing! 🎉

---

**Need help?** Check [Zoom API Documentation](https://developers.zoom.us/docs/api/)
