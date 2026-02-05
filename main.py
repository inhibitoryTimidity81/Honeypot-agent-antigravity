"""
Main FastAPI Application
Agentic Honeypot for Scam Detection & Intelligence Extraction
"""
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Import our modules
from scam_detector import ScamDetector
from agent import honeypot_agent
from intelligence_extractor import intelligence_extractor
from session_manager import session_manager
from guvi_callback import guvi_callback

# Load environment variables
load_dotenv()

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
    agentResponse: Optional[str] = None
    engagementMetrics: Optional[EngagementMetrics] = None
    extractedIntelligence: Optional[ExtractedIntelligence] = None
    agentNotes: Optional[str] = None


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


@app.post("/api/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
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
        
        # Update session with scam detection result
        if is_scam and not session.scam_detected:
            session.scam_detected = True
            session.agent_notes = f"Initial scam type: {scam_type}"
        
        # Extract intelligence from current message
        intelligence_extractor.update_intelligence(
            existing=session.intelligence.to_dict(),
            new_message=current_message.text
        )
        
        # Update session intelligence
        all_messages = [
            {"sender": msg.sender, "text": msg.text}
            for msg in session.messages
        ]
        extracted = intelligence_extractor.extract_all(all_messages)
        
        session.intelligence.bankAccounts = extracted['bankAccounts']
        session.intelligence.upiIds = extracted['upiIds']
        session.intelligence.phishingLinks = extracted['phishingLinks']
        session.intelligence.phoneNumbers = extracted['phoneNumbers']
        session.intelligence.suspiciousKeywords = extracted['suspiciousKeywords']
        
        # Generate agent response if scam detected
        agent_response = None
        if is_scam and scam_detector.should_engage(confidence):
            agent_response = honeypot_agent.generate_response(
                current_message=current_message.text,
                conversation_history=conversation_history,
                scam_type=scam_type,
                metadata=metadata.dict() if metadata else None
            )
            
            # Add agent response to session
            session.add_message(
                sender="user",
                text=agent_response,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"Generated agent response: {agent_response}")
        
        # Check if conversation should end
        should_end, end_reason = honeypot_agent.should_end_conversation(
            conversation_history=all_messages,
            intelligence_extracted=session.intelligence.to_dict()
        )
        
        # If conversation should end, send GUVI callback
        if should_end and session.scam_detected and not session.is_completed:
            logger.info(f"Ending conversation for session {session_id}: {end_reason}")
            
            # Generate final agent notes
            session.agent_notes = honeypot_agent.generate_agent_notes(
                conversation_history=all_messages,
                scam_type=scam_type,
                intelligence=session.intelligence.to_dict()
            )
            
            # Send callback to GUVI
            callback_success = guvi_callback.send_final_result(
                session_id=session_id,
                scam_detected=session.scam_detected,
                total_messages=session.get_total_messages(),
                intelligence=session.intelligence.to_dict(),
                agent_notes=session.agent_notes
            )
            
            if callback_success:
                session_manager.mark_completed(session_id)
                logger.info(f"Session {session_id} completed and callback sent")
            else:
                logger.error(f"Failed to send GUVI callback for session {session_id}")
        
        # Build response
        response = HoneypotResponse(
            status="success",
            scamDetected=session.scam_detected,
            agentResponse=agent_response,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=session.get_engagement_duration(),
                totalMessagesExchanged=session.get_total_messages()
            ),
            extractedIntelligence=ExtractedIntelligence(**session.intelligence.to_dict()),
            agentNotes=session.agent_notes
        )
        
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
