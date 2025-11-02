# Partner API Integration Guide

## Overview

The Partner API allows authorized external organizations to transfer leads to our AI Outbound Meeting Scheduler platform via secure API endpoints.

### Key Features

- **Secure Authentication**: API key-based authentication
- **Bulk Transfer**: Submit multiple leads in a single request
- **Rate Limiting**: Protect platform from abuse
- **Automatic Language Detection**: Auto-detect language from phone numbers
- **Duplicate Prevention**: Skip leads with existing phone numbers
- **Detailed Error Reporting**: Get specific feedback for each lead

---

## Getting Started

### 1. Obtain API Credentials

Contact your platform administrator to:
1. Create a partner account for your organization
2. Receive your unique API key
3. Configure your rate limit (default: 100 leads per minute)

**IMPORTANT**: Your API key is shown only once during creation. Store it securely!

### 2. API Endpoint

**Base URL**: `https://your-platform.com`

**Transfer Endpoint**: `POST /api/leads/partner-transfer`

---

## Authentication

All API requests must include your API key in the request headers.

### Header Format

```
X-API-Key: your_api_key_here
```

### Example (cURL)

```bash
curl -X POST https://your-platform.com/api/leads/partner-transfer \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{"leads": [...]}'
```

---

## API Reference

### Transfer Leads

**Endpoint**: `POST /api/leads/partner-transfer`

**Authentication**: Required (API Key)

**Rate Limit**: Based on your partner configuration (default 100 leads/minute)

#### Request Body

```json
{
  "leads": [
    {
      "name": "John Doe",
      "phone": "+1234567890",
      "email": "john@example.com"
    },
    {
      "name": "Jane Smith",
      "phone": "+1987654321",
      "email": "jane@example.com"
    }
  ]
}
```

#### Request Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `leads` | Array | Yes | Array of lead objects |
| `leads[].name` | String | Yes | Lead's full name |
| `leads[].phone` | String | Yes | Lead's phone number (international format recommended) |
| `leads[].email` | String | No | Lead's email address |

#### Phone Number Format

**Recommended**: Use international format with country code

✅ **Good Examples**:
- `+1234567890` (USA)
- `+442071234567` (UK)
- `+33123456789` (France)

⚠️ **Acceptable**:
- `234567890` (system will attempt to parse)

❌ **Avoid**:
- Letters or special characters (except `+`)

#### Response

**Success (200 OK)**:

```json
{
  "success": true,
  "total_submitted": 10,
  "created": 8,
  "skipped": 2,
  "failed": 0,
  "errors": [
    {
      "index": 3,
      "phone": "+1234567890",
      "reason": "Phone number already exists (Lead ID: 42)"
    },
    {
      "index": 7,
      "phone": "+1111111111",
      "reason": "Phone number already exists (Lead ID: 89)"
    }
  ],
  "message": "Successfully processed 8 out of 10 leads"
}
```

**Response Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `success` | Boolean | Overall success status |
| `total_submitted` | Integer | Total leads in request |
| `created` | Integer | Number of leads successfully created |
| `skipped` | Integer | Number of duplicate leads skipped |
| `failed` | Integer | Number of leads that failed processing |
| `errors` | Array | Details of skipped/failed leads (if any) |
| `errors[].index` | Integer | Index in submitted array (0-based) |
| `errors[].phone` | String | Phone number that caused error |
| `errors[].reason` | String | Error description |
| `message` | String | Human-readable summary |

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `200` | Success | Request processed (check response for per-lead status) |
| `401` | Unauthorized | Check your API key is correct and included in `X-API-Key` header |
| `403` | Forbidden | Your partner account is disabled. Contact support. |
| `429` | Too Many Requests | Rate limit exceeded. Wait and retry. |
| `500` | Server Error | Contact support with request details |

### Common Error Reasons

| Reason | Cause | Solution |
|--------|-------|----------|
| "Phone number already exists (Lead ID: X)" | Duplicate phone | This is expected. Lead already in system. |
| "Invalid phone format" | Malformed phone number | Use international format with `+` |
| "Missing required fields" | Missing name or phone | Ensure all required fields present |

---

## Rate Limiting

- **Window**: 60 seconds (rolling)
- **Default Limit**: 100 leads per minute
- **Custom Limits**: Contact admin to adjust based on your needs

**Best Practices**:
- Batch leads into groups (e.g., 50-100 per request)
- Implement exponential backoff on 429 errors
- Monitor response times

---

## Code Examples

### Python

```python
import requests
import json

API_URL = "https://your-platform.com/api/leads/partner-transfer"
API_KEY = "your_api_key_here"

def transfer_leads(leads):
    """
    Transfer leads to platform.

    Args:
        leads: List of dicts with keys: name, phone, email (optional)

    Returns:
        Response dict with transfer results
    """
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    payload = {
        "leads": leads
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()  # Raise error for bad status codes

    return response.json()


# Example usage
leads_to_transfer = [
    {
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john@example.com"
    },
    {
        "name": "Jane Smith",
        "phone": "+1987654321",
        "email": "jane@example.com"
    }
]

try:
    result = transfer_leads(leads_to_transfer)
    print(f"Success! Created {result['created']} leads")
    if result['errors']:
        print(f"Errors/Skips: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error['phone']}: {error['reason']}")
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const API_URL = 'https://your-platform.com/api/leads/partner-transfer';
const API_KEY = 'your_api_key_here';

async function transferLeads(leads) {
  try {
    const response = await axios.post(
      API_URL,
      { leads },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        }
      }
    );

    const result = response.data;
    console.log(`Success! Created ${result.created} leads`);

    if (result.errors && result.errors.length > 0) {
      console.log(`Errors/Skips: ${result.errors.length}`);
      result.errors.forEach(error => {
        console.log(`  - ${error.phone}: ${error.reason}`);
      });
    }

    return result;
  } catch (error) {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status);
      console.error('Details:', error.response.data);
    } else {
      // Network or other error
      console.error('Error:', error.message);
    }
    throw error;
  }
}

// Example usage
const leadsToTransfer = [
  {
    name: 'John Doe',
    phone: '+1234567890',
    email: 'john@example.com'
  },
  {
    name: 'Jane Smith',
    phone: '+1987654321',
    email: 'jane@example.com'
  }
];

transferLeads(leadsToTransfer);
```

### cURL

```bash
#!/bin/bash

API_URL="https://your-platform.com/api/leads/partner-transfer"
API_KEY="your_api_key_here"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "leads": [
      {
        "name": "John Doe",
        "phone": "+1234567890",
        "email": "john@example.com"
      },
      {
        "name": "Jane Smith",
        "phone": "+1987654321",
        "email": "jane@example.com"
      }
    ]
  }' \
  | json_pp  # Pretty print JSON response
```

---

## Best Practices

### 1. Batch Requests Efficiently

**DO**:
```python
# Send 50-100 leads per request
batch_size = 50
for i in range(0, len(all_leads), batch_size):
    batch = all_leads[i:i + batch_size]
    transfer_leads(batch)
    time.sleep(1)  # Small delay between batches
```

**DON'T**:
```python
# Don't send one lead at a time
for lead in all_leads:
    transfer_leads([lead])  # Inefficient!
```

### 2. Handle Errors Gracefully

```python
try:
    result = transfer_leads(leads)

    # Log successful creates
    log_success(result['created'])

    # Handle skipped duplicates (not a failure!)
    if result['skipped'] > 0:
        log_info(f"Skipped {result['skipped']} existing leads")

    # Handle real failures
    if result['failed'] > 0:
        log_error(f"Failed to process {result['failed']} leads")
        for error in result['errors']:
            if 'already exists' not in error['reason']:
                # Only alert on non-duplicate errors
                alert_team(error)

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Rate limit - wait and retry
        time.sleep(60)
        retry_request()
    elif e.response.status_code == 401:
        # Bad API key
        alert_team("Invalid API credentials!")
    else:
        # Other error
        log_error(e)
```

### 3. Validate Before Sending

```python
def validate_lead(lead):
    """Validate lead before sending to API"""
    if not lead.get('name') or not lead.get('phone'):
        return False, "Missing required fields"

    # Basic phone validation
    phone = lead['phone']
    if not phone.startswith('+'):
        lead['phone'] = f"+{phone}"  # Add + if missing

    # Email validation (if provided)
    if lead.get('email'):
        if '@' not in lead['email']:
            return False, "Invalid email format"

    return True, None

# Filter valid leads before transfer
valid_leads = []
for lead in all_leads:
    is_valid, error = validate_lead(lead)
    if is_valid:
        valid_leads.append(lead)
    else:
        log_warning(f"Invalid lead skipped: {error}")

transfer_leads(valid_leads)
```

### 4. Monitor and Log

```python
import logging

# Log all API interactions
logging.info(f"Transferring {len(leads)} leads to platform")

result = transfer_leads(leads)

logging.info(f"Transfer complete: {result['created']} created, "
             f"{result['skipped']} skipped, {result['failed']} failed")

# Track metrics
metrics.increment('leads_transferred', result['created'])
metrics.increment('leads_skipped', result['skipped'])
metrics.increment('leads_failed', result['failed'])
```

---

## Security Best Practices

### 1. Protect Your API Key

**DO**:
- Store API key in environment variables
- Use secret management systems (AWS Secrets Manager, etc.)
- Never commit API keys to version control
- Rotate keys periodically

**DON'T**:
- Hardcode API keys in source code
- Share API keys via email or chat
- Use the same API key across multiple systems

### 2. Use HTTPS Only

All API requests must use HTTPS. HTTP requests will be rejected.

### 3. Implement Retry Logic with Backoff

```python
import time

def transfer_with_retry(leads, max_retries=3):
    for attempt in range(max_retries):
        try:
            return transfer_leads(leads)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit - exponential backoff
                wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                time.sleep(wait_time)
                continue
            else:
                raise

    raise Exception("Max retries exceeded")
```

---

## Testing Your Integration

### 1. Interactive API Documentation

Visit `https://your-platform.com/docs` for:
- Interactive API explorer
- Try endpoints in your browser
- See real-time schema validation

### 2. Test with Small Batches

Start with 5-10 leads to verify:
- Authentication works
- Phone format is correct
- Error handling works

### 3. Monitor First Production Run

- Start with a small batch (50-100 leads)
- Check response carefully
- Verify leads appear in platform
- Monitor rate limits

---

## FAQ

### Q: What happens to duplicate phone numbers?

**A**: They are automatically skipped and reported in the `errors` array. The existing lead remains unchanged.

### Q: Can I update existing leads via the API?

**A**: No. This endpoint only creates new leads. Duplicates are skipped.

### Q: What phone number formats are supported?

**A**: All international formats. Recommended: `+[country_code][number]` (e.g., `+1234567890`)

### Q: How do I know which partner account submitted a lead?

**A**: All leads are automatically tagged with your partner ID for tracking and analytics.

### Q: Can I retrieve leads I've submitted?

**A**: Not via API currently. Contact admin for reporting/analytics.

### Q: What if my rate limit is too low?

**A**: Contact admin to discuss increasing your rate limit based on your needs.

### Q: Can I get a webhook when a meeting is booked from my leads?

**A**: Not currently supported. Contact admin to discuss custom integrations.

---

## Support

### Getting Help

- **Technical Issues**: Contact support@your-platform.com
- **API Key Reset**: Contact your account manager
- **Rate Limit Increase**: Submit request with expected volume

### Changelog

**Version 1.0.0** (2025-01-03)
- Initial release
- Bulk lead transfer endpoint
- API key authentication
- Rate limiting

---

## Appendix: Response Examples

### Successful Transfer (All Leads Created)

```json
{
  "success": true,
  "total_submitted": 5,
  "created": 5,
  "skipped": 0,
  "failed": 0,
  "errors": null,
  "message": "Successfully processed 5 out of 5 leads"
}
```

### Partial Success (Some Duplicates)

```json
{
  "success": true,
  "total_submitted": 10,
  "created": 7,
  "skipped": 3,
  "failed": 0,
  "errors": [
    {
      "index": 2,
      "phone": "+1234567890",
      "reason": "Phone number already exists (Lead ID: 42)"
    },
    {
      "index": 5,
      "phone": "+1111111111",
      "reason": "Phone number already exists (Lead ID: 89)"
    },
    {
      "index": 8,
      "phone": "+1222222222",
      "reason": "Phone number already exists (Lead ID: 103)"
    }
  ],
  "message": "Successfully processed 7 out of 10 leads"
}
```

### Authentication Error

```json
{
  "detail": "Invalid API key"
}
```
*HTTP Status: 401*

### Rate Limit Exceeded

```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per 60 seconds."
}
```
*HTTP Status: 429*

---

**Last Updated**: January 3, 2025
**API Version**: 1.0.0
