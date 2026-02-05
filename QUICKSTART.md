# 🚀 Quick Start Guide

## For Immediate Deployment

### Step 1: Get API Key
Go to https://ai.google.dev and get your Google Gemini API key

### Step 2: Configure
```bash
copy .env.example .env
```
Edit `.env` and add your keys:
```
GOOGLE_API_KEY=your_gemini_key_here
API_KEY=choose_a_secure_password
```

### Step 3: Deploy to Railway

1. Push to GitHub:
```bash
git init
git add .
git commit -m "Honeypot deployment"
git push origin main
```

2. Go to https://railway.app
3. New Project → Deploy from GitHub
4. Add environment variables (same as .env)
5. Deploy!

### Step 4: Get Your URL

Railway will give you: `https://your-app.railway.app`

**Your submission URL**: `https://your-app.railway.app/api/honeypot`

**Your API key**: Whatever you set in `API_KEY`

---

## Test Locally First

```bash
pip install -r requirements.txt
python main.py
```

Visit: http://localhost:8000/health

---

## Need Help?

See `walkthrough.md` for detailed instructions.

---

## What You're Submitting

- **Endpoint**: `https://your-app.railway.app/api/honeypot`
- **Method**: POST
- **Auth Header**: `x-api-key: your_api_key`
- **Content-Type**: application/json

The system automatically:
✅ Detects scams
✅ Engages scammers
✅ Extracts intelligence
✅ Reports to GUVI

**You're done! 🎉**
