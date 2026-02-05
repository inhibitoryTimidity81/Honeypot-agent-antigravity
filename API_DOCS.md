# API Documentation

## Overview

The Agentic Honeypot API provides an intelligent system for detecting and engaging with scam messages. It uses AI to maintain human-like conversations while extracting valuable intelligence about scammers.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Production**: `https://your-app.railway.app` or `https://your-app.onrender.com`

## Authentication

All API requests require authentication using an API key in the request header:

```
x-api-key: your_custom_api_key_here
```

## Endpoints

### GET /

Root endpoint providing API information.

**Response:**
```json
{
  "name": "Agentic Honeypot API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {
    "health": "/health",
    "honeypot": "/api/honeypot"
  }
}
```

### GET /health

Health check endpoint to verify API status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-05T10:00:00Z",
  "services": {
    "scam_detector": "operational",
    "ai_agent": "operational",
    "session_manager": "operational"
  }
}
```

### POST /api/honeypot

Main endpoint for processing scam messages and engaging with scammers.

**Headers:**
- `x-api-key`: Your API key (required)
- `Content-Type`: application/json

**Request Body:**

```json
{
  "sessionId": "string (required)",
  "message": {
    "sender": "string (required) - 'scammer' or 'user'",
    "text": "string (required) - message content",
    "timestamp": "string (required) - ISO-8601 format"
  },
  "conversationHistory": [
    {
      "sender": "string",
      "text": "string",
      "timestamp": "string"
    }
  ],
  "metadata": {
    "channel": "string (optional) - SMS/WhatsApp/Email/Chat",
    "language": "string (optional) - default: English",
    "locale": "string (optional) - default: IN"
  }
}
```

**Response:**

```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "string - AI agent's response to the scammer",
  "engagementMetrics": {
    "engagementDurationSeconds": 120,
    "totalMessagesExchanged": 5
  },
  "extractedIntelligence": {
    "bankAccounts": ["1234567890"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://malicious-site.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify", "blocked"]
  },
  "agentNotes": "Scam type: bank_fraud. Tactics used: urgency tactics, verification requests"
}
```

**Error Responses:**

- **401 Unauthorized**: Invalid API key
  ```json
  {
    "detail": "Invalid API key"
  }
  ```

- **500 Internal Server Error**: Server error
  ```json
  {
    "status": "error",
    "message": "An unexpected error occurred",
    "detail": "Error description"
  }
  ```

## Request Examples

### First Message (New Conversation)

```bash
curl -X POST https://your-app.railway.app/api/honeypot \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify now.",
      "timestamp": "2026-02-05T10:00:00Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Follow-up Message

```bash
curl -X POST https://your-app.railway.app/api/honeypot \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-123",
    "message": {
      "sender": "scammer",
      "text": "Share your UPI ID to verify",
      "timestamp": "2026-02-05T10:05:00Z"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your bank account will be blocked. Verify now.",
        "timestamp": "2026-02-05T10:00:00Z"
      },
      {
        "sender": "user",
        "text": "Why will my account be blocked?",
        "timestamp": "2026-02-05T10:02:00Z"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

## GUVI Integration

When the system determines that sufficient intelligence has been extracted, it automatically sends a callback to the GUVI evaluation endpoint:

**Endpoint:** `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

**Payload:**
```json
{
  "sessionId": "session-123",
  "scamDetected": true,
  "totalMessagesExchanged": 15,
  "extractedIntelligence": {
    "bankAccounts": ["1234567890"],
    "upiIds": ["scammer@paytm"],
    "phishingLinks": ["http://malicious.com"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

## Rate Limiting

Currently, there are no rate limits, but it's recommended to:
- Use unique session IDs for each conversation
- Avoid sending more than 50 messages per session
- Allow at least 1 second between messages

## Best Practices

1. **Session Management**: Use unique, descriptive session IDs
2. **Conversation History**: Always include previous messages for context
3. **Metadata**: Provide channel and language information when available
4. **Error Handling**: Implement retry logic for network failures
5. **Testing**: Test with various scam scenarios before production use

## Scam Types Detected

The system can detect and engage with:
- Bank fraud
- UPI fraud
- Phishing attempts
- Fake customer service
- Prize/lottery scams
- Investment scams
- OTP/PIN requests
- Payment redirection
- Fake delivery scams

## Support

For issues or questions:
- Check the logs for detailed error messages
- Verify API key is correct
- Ensure request format matches documentation
- Test with the health endpoint first
