# Google Domain-Wide Delegation Setup Guide

This guide explains how to enable Domain-Wide Delegation so your service account can create Google Meet links.

## Prerequisites

✅ **Google Workspace** account (not free Gmail)
✅ **Admin access** to Google Workspace
✅ Service account already created (you have this: `callcenter@callcenter-477010.iam.gserviceaccount.com`)

---

## Step 1: Enable Domain-Wide Delegation in Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: **callcenter-477010**
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Find: `callcenter@callcenter-477010.iam.gserviceaccount.com`
5. Click **"Show Domain-Wide Delegation"** (expand the section)
6. Check **"Enable Google Workspace Domain-Wide Delegation"**
7. Click **Save**

---

## Step 2: Authorize in Google Workspace Admin Console

**Important:** You must be a Google Workspace admin.

1. Go to [Google Workspace Admin Console](https://admin.google.com/)
2. Navigate to: **Security** → **Access and data control** → **API Controls**
3. Scroll to **"Domain wide delegation"** section
4. Click **"Manage Domain Wide Delegation"**
5. Click **"Add new"**
6. Fill in the form:

   **Client ID:**
   ```
   105991917380105552378
   ```

   **OAuth Scopes:**
   ```
   https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/calendar.events
   ```

7. Click **"Authorize"**

---

## Step 3: Update Your .env File

Add this line to your `.env` file:

```bash
# Replace with a real user email in your Google Workspace domain
GOOGLE_DELEGATED_USER_EMAIL=admin@yourdomain.com
```

**Important:** This must be a real user in your Google Workspace domain. The service account will act on behalf of this user.

**Examples:**
- `admin@altaai.com` (if your domain is altaai.com)
- `calendar@yourcompany.com` (dedicated calendar user)
- Any valid Google Workspace user email

---

## Step 4: Restart Your Application

```bash
# Restart backend server
# The service account will now impersonate the delegated user
```

---

## Step 5: Test Google Meet Link Creation

Run this test to verify it works:

```python
from backend.services.calendar_service import CalendarService

calendar = CalendarService()
meet_link = calendar.create_google_meet_link()

if meet_link:
    print(f"✅ SUCCESS! Google Meet link: {meet_link}")
else:
    print("❌ FAILED - Check logs for errors")
```

---

## What This Enables

✅ Service account can create Google Meet links
✅ Service account can add attendees to events
✅ Service account can send calendar invitations
✅ All calendar events created on behalf of the delegated user

---

## Troubleshooting

### Error: "Invalid conference type value"
**Cause:** Not impersonating a Google Workspace user
**Fix:** Make sure `GOOGLE_DELEGATED_USER_EMAIL` is set in `.env`

### Error: "Not Authorized to access this resource/api"
**Cause:** Domain-Wide Delegation not properly configured
**Fix:**
1. Verify Client ID is correct: `105991917380105552378`
2. Verify OAuth scopes include both calendar scopes
3. Wait 5-10 minutes for changes to propagate

### Error: "User not found"
**Cause:** Delegated user email doesn't exist in your domain
**Fix:** Use a real Google Workspace user email

### Still using group calendar
**Cause:** `GOOGLE_CALENDAR_ID` still points to group calendar
**Fix:** Change to `primary` or a specific user's email:
```bash
GOOGLE_CALENDAR_ID=primary
# OR
GOOGLE_CALENDAR_ID=admin@yourdomain.com
```

---

## Security Considerations

- ⚠️ The service account will have full calendar access for the delegated user
- ⚠️ Choose a dedicated calendar user (not your personal admin account)
- ⚠️ Consider creating a `calendar@yourdomain.com` user specifically for this purpose
- ⚠️ Service account credentials must be kept secure (never commit to git)

---

## Alternative: Use OAuth Instead

If you can't use Domain-Wide Delegation:

1. Don't set `GOOGLE_DELEGATED_USER_EMAIL`
2. Use OAuth authentication (credentials.json + token.json)
3. Set `GOOGLE_CALENDAR_ID=primary`
4. Google Meet links will work with personal Gmail calendars

**Limitation:** OAuth requires manual re-authentication every time the token expires.

---

## Your Service Account Details

**Project:** callcenter-477010
**Service Account Email:** callcenter@callcenter-477010.iam.gserviceaccount.com
**Client ID:** 105991917380105552378
**Required Scopes:**
- `https://www.googleapis.com/auth/calendar`
- `https://www.googleapis.com/auth/calendar.events`

---

## Next Steps

After setup:
1. Test creating a Google Meet link
2. Test booking a meeting (should include Meet link now)
3. Verify calendar invitations are sent
4. Check that Meet links work

---

**Need help?** Contact Google Workspace support or check [Google Workspace Admin Help](https://support.google.com/a/answer/162106)
