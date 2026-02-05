"""
GUVI Callback Module
Sends final results to GUVI evaluation endpoint
"""
import os
import requests
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class GUVICallback:
    """Handles callbacks to GUVI evaluation endpoint"""
    
    def __init__(self):
        self.callback_url = os.getenv(
            "GUVI_CALLBACK_URL",
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
        )
    
    def send_final_result(
        self,
        session_id: str,
        scam_detected: bool,
        total_messages: int,
        intelligence: Dict,
        agent_notes: str
    ) -> bool:
        """
        Send final result to GUVI endpoint
        
        Args:
            session_id: Unique session identifier
            scam_detected: Whether scam was detected
            total_messages: Total messages exchanged
            intelligence: Extracted intelligence dictionary
            agent_notes: Summary of agent observations
        
        Returns:
            True if callback successful, False otherwise
        """
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intelligence,
            "agentNotes": agent_notes
        }
        
        try:
            logger.info(f"Sending final result to GUVI for session {session_id}")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(
                self.callback_url,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully sent callback for session {session_id}")
                return True
            else:
                logger.error(
                    f"GUVI callback failed with status {response.status_code}: {response.text}"
                )
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"GUVI callback timeout for session {session_id}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"GUVI callback error for session {session_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in GUVI callback: {e}")
            return False


# Global callback instance
guvi_callback = GUVICallback()
