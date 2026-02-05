# Deployment Guide

## Quick Deployment Summary

### Railway (Recommended - Fastest)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Agentic Honeypot System"
   git push origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - New Project → Deploy from GitHub
   - Select repository
   - Add environment variables:
     - `GOOGLE_API_KEY`
     - `API_KEY`
   - Deploy automatically

3. **Get URL**
   - Settings → Generate Domain
   - URL: `https://your-app.railway.app`

**Submission URL**: `https://your-app.railway.app/api/honeypot`

---

### Render (Alternative)

1. **Push to GitHub** (same as above)

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect repository
   - Add environment variables
   - Deploy

3. **Get URL**
   - URL: `https://your-app.onrender.com`

**Submission URL**: `https://your-app.onrender.com/api/honeypot`

---

## Environment Variables Required

```
GOOGLE_API_KEY=your_gemini_api_key
API_KEY=your_custom_api_key
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

---

## Testing Your Deployment

### Health Check
```bash
curl https://your-app.railway.app/health
```

### Test Scam Detection
```bash
curl -X POST https://your-app.railway.app/api/honeypot \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test-1","message":{"sender":"scammer","text":"Your account will be blocked","timestamp":"2026-02-05T10:00:00Z"},"conversationHistory":[]}'
```

---

## What to Submit to GUVI

**Endpoint**: `https://your-app.railway.app/api/honeypot`

**Authentication**: `x-api-key: your_custom_api_key`

**Method**: POST

**Content-Type**: application/json

---

## Troubleshooting

### Deployment fails
- Check logs in Railway/Render dashboard
- Verify all environment variables are set
- Ensure requirements.txt is present

### API returns 401
- Check API key is correct
- Verify header is `x-api-key` (with hyphen)

### No agent response
- Check Google API key is valid
- Verify API quota is not exceeded
- Check logs for errors

---

## Support

See `walkthrough.md` for detailed instructions.
