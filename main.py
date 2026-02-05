"""
Main FastAPI Application
Agentic Honeypot for Scam Detection & Intelligence Extraction
"""
from fastapi import FastAPI, HTTPException, Header, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

# Import our modules
from scam_detector import ScamDetector
from agent import honeypot_agent
from hybrid_intelligence_extractor import hybrid_extractor
from session_manager import session_manager
from guvi_callback import guvi_callback

# # Load environment variables
# load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honeypot API",
    description="AI-powered honeypot for scam detection and intelligence extraction",
    version="1.0.0"
)

# Initialize scam detector
scam_detector = ScamDetector()

# Get API key from environment
API_KEY = os.getenv("API_KEY", "your_custom_api_key_here")


# Pydantic models for request/response
class Message(BaseModel):
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class Metadata(BaseModel):
    channel: Optional[str] = Field(None, description="Communication channel")
    language: Optional[str] = Field("English", description="Message language")
    locale: Optional[str] = Field("IN", description="Country/region code")


class HoneypotRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Current incoming message")
    conversationHistory: List[Dict] = Field(
        default_factory=list,
        description="Previous messages in conversation"
    )
    metadata: Optional[Metadata] = Field(None, description="Additional context")


class EngagementMetrics(BaseModel):
    engagementDurationSeconds: int
    totalMessagesExchanged: int


class ExtractedIntelligence(BaseModel):
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)


class HoneypotResponse(BaseModel):
    status: str = "success"
    scamDetected: bool
    engagementMetrics: EngagementMetrics
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str


# API Key authentication
async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Agentic Honeypot API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "honeypot": "/api/honeypot"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scam_detector": "operational",
            "ai_agent": "operational",
            "session_manager": "operational"
        }
    }


async def send_guvi_callback_background(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: Dict,
    agent_notes: str
):
    """
    Send final result callback to GUVI in background
    This runs as a background task and does not block the response
    """
    callback_url = os.getenv(
        "GUVI_CALLBACK_URL",
        "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    )
    
    payload = {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": intelligence,
        "agentNotes": agent_notes
    }
    
    try:
        logger.info(f"Sending GUVI callback for session {session_id}")
        logger.debug(f"Callback payload: {payload}")
        
        response = requests.post(
            callback_url,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"✅ GUVI callback successful for session {session_id}")
        else:
            logger.error(f"❌ GUVI callback failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ GUVI callback timeout for session {session_id}")
    except Exception as e:
        logger.error(f"❌ GUVI callback error for session {session_id}: {e}")


@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(..., alias="x-api-key")
):
    """
    Main honeypot endpoint for processing scam messages
    
    This endpoint:
    1. Receives incoming messages
    2. Detects scam intent
    3. Activates AI agent if scam detected
    4. Generates human-like responses
    5. Extracts intelligence
    6. Sends callback to GUVI when conversation completes
    """
    # Verify API key
    await verify_api_key(x_api_key)
    
    session_id = request.sessionId
    current_message = request.message
    conversation_history = request.conversationHistory
    metadata = request.metadata
    
    logger.info(f"Processing message for session {session_id}")
    
    try:
        # Get or create session
        session = session_manager.get_or_create_session(session_id)
        
        # Add current message to session
        session.add_message(
            sender=current_message.sender,
            text=current_message.text,
            timestamp=current_message.timestamp
        )
        
        # Detect scam intent
        is_scam, confidence, scam_type = scam_detector.detect_scam(
            message=current_message.text,
            conversation_history=conversation_history
        )
        
        logger.info(f"Scam detection: is_scam={is_scam}, confidence={confidence}, type={scam_type}")
        
        # Update session with scam detection result (only if first time detecting scam)
        if is_scam and not session.scam_detected:
            session.scam_detected = True
            session.scam_type = scam_type
            logger.info(f"Scam detected for first time in session {session_id}: {scam_type}")
        
        # Extract intelligence ONLY if scam is detected in session
        if session.scam_detected:
            all_messages_text = " ".join([msg.text for msg in session.messages])
            extracted = hybrid_extractor.extract_intelligence_hybrid(all_messages_text)
            
            # Update session intelligence
            session.intelligence.bankAccounts = extracted['bankAccounts']
            session.intelligence.upiIds = extracted['upiIds']
            session.intelligence.phishingLinks = extracted['phishingLinks']
            session.intelligence.phoneNumbers = extracted['phoneNumbers']
            session.intelligence.suspiciousKeywords = extracted['suspiciousKeywords']
            
            logger.info(f"Extracted intelligence: {len(extracted['bankAccounts'])} accounts, "
                       f"{len(extracted['upiIds'])} UPIs, {len(extracted['phoneNumbers'])} phones, "
                       f"{len(extracted['phishingLinks'])} links")
        else:
            # For normal conversations, keep intelligence empty
            logger.info("Normal conversation - no intelligence extraction")
        
        # ALWAYS generate agent response (choose mode based on session scam state)
        agent_response = None
        if session.scam_detected:
            # Scam was detected in this session - use vulnerable mode
            agent_response = honeypot_agent.generate_response(
                current_message=current_message.text,
                conversation_history=conversation_history,
                scam_type=session.scam_type,
                metadata=metadata.dict() if metadata else None
            )
            logger.info(f"Generated vulnerable mode response: {agent_response}")
        else:
            # No scam detected yet - use normal conversation mode
            agent_response = honeypot_agent.generate_normal_response(
                current_message=current_message.text,
                conversation_history=conversation_history,
                metadata=metadata.dict() if metadata else None
            )
            logger.info(f"Generated normal mode response: {agent_response}")
        
        # Add agent response to session
        if agent_response:
            session.add_message(
                sender="user",
                text=agent_response,
                timestamp=datetime.now().isoformat()
            )
        
        # Generate RICH agent notes if scam detected
        if session.scam_detected:
            all_messages = [
                {"sender": msg.sender, "text": msg.text}
                for msg in session.messages
            ]
            session.agent_notes = honeypot_agent.generate_agent_notes(
                conversation_history=all_messages,
                scam_type=session.scam_type,
                intelligence=session.intelligence.to_dict()
            )
        else:
            session.agent_notes = "No scam detected. Normal conversation."
        
        # Schedule BACKGROUND CALLBACK ONLY if scam detected
        # This sends results to judges on EVERY turn where scamDetected=True
        if session.scam_detected:
            background_tasks.add_task(
                send_guvi_callback_background,
                session_id=session_id,
                scam_detected=True,
                total_messages=session.get_total_messages(),
                intelligence=session.intelligence.to_dict(),
                agent_notes=session.agent_notes
            )
            logger.info(f"📤 Scheduled background callback for session {session_id}")
        
        # Build STRICT response (immediate HTTP 200)
        # Return scamDetected based on SESSION state, not current message
        response = HoneypotResponse(
            status="success",
            scamDetected=session.scam_detected,  # Session-level scam detection
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=session.get_engagement_duration(),
                totalMessagesExchanged=session.get_total_messages()
            ),
            extractedIntelligence=ExtractedIntelligence(**session.intelligence.to_dict()),
            agentNotes=session.agent_notes
        )
        
        logger.info(f"✅ Returning response for session {session_id} (scamDetected={session.scam_detected})")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request for session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting Agentic Honeypot API on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
