# Agentic Honeypot API

Production-ready AI-powered honeypot system for detecting scam messages, engaging scammers autonomously, and extracting intelligence.

## 🎯 Features

- **Intelligent Scam Detection**: Uses Google Gemini AI to detect various scam types
- **Autonomous Engagement**: AI agent maintains human-like conversations with scammers
- **Intelligence Extraction**: Automatically extracts bank accounts, UPI IDs, phone numbers, and phishing links
- **Image Request Handling**: Responds intelligently to requests for documents/images
- **GUVI Integration**: Automatically sends results to GUVI evaluation endpoint
- **Production Ready**: Includes deployment configs for Railway and Render

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API Key ([Get one here](https://ai.google.dev))

### Local Setup

1. **Clone the repository**
   ```bash
   cd Honey-pot-antigravity
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key
   API_KEY=your_custom_api_key_for_authentication
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

5. **Test the API**
   ```bash
   curl -X GET http://localhost:8000/health
   ```

## 🌐 Deployment

### Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select this repository
4. Add environment variables:
   - `GOOGLE_API_KEY`
   - `API_KEY`
5. Railway will automatically deploy using `railway.json` config
6. Your API URL will be: `https://your-app.railway.app`

### Deploy to Render

1. Go to [Render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Add environment variables in the dashboard:
   - `GOOGLE_API_KEY`
   - `API_KEY`
6. Click "Create Web Service"
7. Your API URL will be: `https://your-app.onrender.com`

## 📡 API Usage

### Authentication

All requests require an API key in the header:
```
x-api-key: your_custom_api_key
```

### Endpoint: POST /api/honeypot

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify immediately.",
    "timestamp": "2026-02-05T10:00:00Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "Oh no, really? What do I need to do?",
  "engagementMetrics": {
    "engagementDurationSeconds": 15,
    "totalMessagesExchanged": 2
  },
  "extractedIntelligence": {
    "bankAccounts": [],
    "upiIds": [],
    "phishingLinks": [],
    "phoneNumbers": [],
    "suspiciousKeywords": ["blocked", "verify", "immediately"]
  },
  "agentNotes": "Initial scam type: bank_fraud"
}
```

## 🎓 Submission URL

After deployment, your submission URL will be:

**Railway:** `https://your-app.railway.app/api/honeypot`

**Render:** `https://your-app.onrender.com/api/honeypot`

Submit this URL to the GUVI hackathon platform along with your API key.

## 🧪 Testing

See `test_scam_scenarios.py` for comprehensive test cases.

Run tests locally:
```bash
python test_scam_scenarios.py
```

## 📊 How It Works

1. **Message Received** → API receives scam message
2. **Scam Detection** → AI analyzes message for scam patterns
3. **Agent Activation** → If scam detected, AI agent engages
4. **Conversation** → Agent maintains human-like dialogue
5. **Intelligence Extraction** → System extracts scammer information
6. **GUVI Callback** → Final results sent to evaluation endpoint

## 🔒 Security

- API key authentication on all endpoints
- No real personal information shared
- Ethical engagement boundaries enforced
- Secure environment variable management

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Support

For issues or questions, please open a GitHub issue.
