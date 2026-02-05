# """
# Scam Detector Module
# Uses Google Gemini to detect scam intent in messages
# """
# import os
# import google.generativeai as genai
# from typing import Tuple
# import logging

# logger = logging.getLogger(__name__)


# class ScamDetector:
#     """Detects scam intent in messages using AI"""
    
#     def __init__(self):
#         api_key = os.getenv("GOOGLE_API_KEY")
#         if not api_key:
#             raise ValueError("GOOGLE_API_KEY environment variable not set")
        
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel('gemini-3-flash-preview')
    
#     def detect_scam(self, message: str, conversation_history: list = None) -> Tuple[bool, float, str]:
#         """
#         Detect if a message is a scam
        
#         Args:
#             message: The message to analyze
#             conversation_history: Previous messages in the conversation
        
#         Returns:
#             Tuple of (is_scam, confidence_score, scam_type)
#         """
#         # Build context from conversation history
#         context = ""
#         if conversation_history:
#             context = "Previous conversation:\n"
#             for msg in conversation_history[-5:]:  # Last 5 messages for context
#                 context += f"{msg['sender']}: {msg['text']}\n"
        
#         prompt = f"""You are a scam detection expert. Analyze the following message and determine if it's a scam attempt.

# {context}

# Current message to analyze: "{message}"

# Common scam patterns to look for:
# 1. Bank fraud (account blocking, verification requests, suspicious activity alerts)
# 2. UPI fraud (payment requests, refund scams, wrong payment claims)
# 3. Phishing (fake links, credential requests, urgent action required)
# 4. Impersonation (fake bank/government officials, fake customer service)
# 5. Urgency tactics (immediate action required, time-limited offers)
# 6. Prize/lottery scams (you've won, claim your prize)
# 7. Investment scams (guaranteed returns, quick money)
# 8. OTP/PIN requests
# 9. Payment redirection attempts
# 10. Fake delivery/courier scams

# Respond in this EXACT format:
# SCAM: [YES/NO]
# CONFIDENCE: [0.0-1.0]
# TYPE: [brief scam type description]
# REASONING: [one line explanation]

# Be strict - if there's any indication of scam tactics, mark it as YES."""

#         try:
#             response = self.model.generate_content(prompt)
#             result_text = response.text.strip()
            
#             # Parse the response
#             lines = result_text.split('\n')
#             is_scam = False
#             confidence = 0.0
#             scam_type = "unknown"
            
#             for line in lines:
#                 if line.startswith("SCAM:"):
#                     is_scam = "YES" in line.upper()
#                 elif line.startswith("CONFIDENCE:"):
#                     try:
#                         confidence = float(line.split(':')[1].strip())
#                     except:
#                         confidence = 0.8 if is_scam else 0.2
#                 elif line.startswith("TYPE:"):
#                     scam_type = line.split(':', 1)[1].strip()
            
#             logger.info(f"Scam detection result: is_scam={is_scam}, confidence={confidence}, type={scam_type}")
#             return is_scam, confidence, scam_type
            
#         except Exception as e:
#             logger.error(f"Error in scam detection: {e}")
#             # Default to safe mode - treat as potential scam if detection fails
#             return True, 0.5, "detection_error"
    
#     def should_engage(self, confidence: float, threshold: float = 0.6) -> bool:
#         """
#         Determine if the agent should engage based on confidence score
        
#         Args:
#             confidence: Confidence score from detection
#             threshold: Minimum confidence to engage
        
#         Returns:
#             True if should engage, False otherwise
#         """
#         return confidence >= threshold

"""
Scam Detector Module
Uses Google Gemini to detect scam intent in messages
"""
import os
import google.generativeai as genai
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class ScamDetector:
    """Detects scam intent in messages using AI"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        # FIX: Use a stable model version
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
    
    def detect_scam(self, message: str, conversation_history: list = None) -> Tuple[bool, float, str]:
        # Build context
        context = ""
        if conversation_history:
            context = "Previous conversation:\n"
            for msg in conversation_history[-5:]:
                context += f"{msg.get('sender', 'unknown')}: {msg.get('text', '')}\n"
        
        prompt = f"""You are a scam detection expert. Analyze this message.
        
        {context}
        Current message: "{message}"
        
        Respond in this EXACT format:
        SCAM: [YES/NO]
        CONFIDENCE: [0.0-1.0]
        TYPE: [Bank Fraud/UPI Fraud/Phishing/Lottery/Threat/Other]
        
        If it is a scam, classify the TYPE accurately.
        """

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse response
            is_scam = "SCAM: YES" in result_text.upper()
            
            # Extract Type
            scam_type = "Unknown"
            for line in result_text.split('\n'):
                if line.upper().startswith("TYPE:"):
                    scam_type = line.split(':', 1)[1].strip()
            
            return is_scam, 0.9, scam_type
            
        except Exception as e:
            logger.error(f"AI Detection Failed: {e}")
            # FALLBACK LOGIC
            keywords = {
                "bank_fraud": ["block", "suspend", "kyc", "pan card", "aadhaar"],
                "upi_fraud": ["payment", "refund", "receive", "pin", "scan"],
                "phishing": ["click", "link", "update", "verify"],
            }
            
            msg_lower = message.lower()
            for s_type, keys in keywords.items():
                if any(k in msg_lower for k in keys):
                    return True, 0.5, s_type
            
            # Generic fallback if suspicious words exist but type is unclear
            if any(k in msg_lower for k in ["urgent", "immediately", "act now"]):
                return True, 0.5, "general_scam"
                
            return False, 0.0, "None"