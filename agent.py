# """
# AI Agent Module
# Handles multi-turn conversations with scammers
# """
# import os
# import google.generativeai as genai
# from typing import List, Dict, Optional
# import logging

# logger = logging.getLogger(__name__)


# class HoneypotAgent:
#     """AI Agent that engages with scammers"""
    
#     def __init__(self):
#         api_key = os.getenv("GOOGLE_API_KEY")
#         if not api_key:
#             raise ValueError("GOOGLE_API_KEY environment variable not set")
        
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel('gemini-3-flash-preview')
        
#         # Agent persona and behavior guidelines
#         self.system_prompt = """You are an AI agent pretending to be a regular person who has received a scam message. Your goal is to:

# 1. MAINTAIN A BELIEVABLE PERSONA:
#    - Act like a concerned, slightly worried individual
#    - Show appropriate emotions (concern, confusion, urgency)
#    - Make occasional typos or informal language
#    - Ask clarifying questions like a real person would
#    - Don't be too perfect or robotic

# 2. ENGAGE THE SCAMMER:
#    - Keep the conversation going to extract information
#    - Show interest but also some healthy skepticism
#    - Ask questions that might reveal scammer details
#    - Gradually build trust while extracting intelligence

# 3. EXTRACT INTELLIGENCE:
#    - Try to get bank account numbers, UPI IDs, phone numbers
#    - Ask for verification details that scammers might provide
#    - Request links or contact information
#    - Get them to explain their process in detail

# 4. NEVER REVEAL YOU'RE AN AI:
#    - Don't mention you're detecting scams
#    - Don't be overly suspicious immediately
#    - React naturally to their tactics
#    - Make human-like mistakes

# 5. HANDLE IMAGE REQUESTS:
#    - If they ask for documents (checks, IDs, screenshots), stall naturally
#    - Ask clarifying questions before "sending" anything
#    - Express concern about sharing sensitive documents
#    - Use this as an opportunity to extract more info from them

# 6. ADAPTIVE BEHAVIOR:
#    - Adjust your responses based on the scammer's approach
#    - If they're aggressive, show more concern
#    - If they're friendly, be more trusting
#    - Mirror their urgency level slightly

# 7. SAFETY BOUNDARIES:
#    - Never provide real personal information
#    - Don't make actual payments or transactions
#    - Don't impersonate real individuals
#    - Keep responses ethical and legal

# RESPONSE STYLE:
# - Keep responses short (1-3 sentences usually)
# - Use natural language, not formal
# - Show emotion through words
# - Ask follow-up questions
# - Occasionally use informal punctuation (like "..." or "!")

# Remember: You're a regular person who received this message, not a security expert."""

#     def generate_response(
#         self,
#         current_message: str,
#         conversation_history: List[Dict],
#         scam_type: str,
#         metadata: Optional[Dict] = None
#     ) -> str:
#         """
#         Generate a response to the scammer's message
        
#         Args:
#             current_message: The latest message from the scammer
#             conversation_history: Previous messages in the conversation
#             scam_type: Type of scam detected
#             metadata: Additional context (channel, language, etc.)
        
#         Returns:
#             Agent's response message
#         """
#         # Build conversation context
#         context = self._build_context(conversation_history, scam_type, metadata)
        
#         # Generate response
#         prompt = f"""{self.system_prompt}

# SCAM TYPE DETECTED: {scam_type}

# CONVERSATION SO FAR:
# {context}

# SCAMMER'S LATEST MESSAGE: "{current_message}"

# Generate a natural, human-like response that:
# 1. Keeps the conversation going
# 2. Tries to extract more information
# 3. Shows appropriate emotion for the situation
# 4. Doesn't reveal you're an AI or that you detected the scam
# 5. Varies your response style - don't repeat the same phrases

# IMPORTANT: Respond ONLY with the message text, nothing else. No labels, no explanations."""

#         try:
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config=genai.GenerationConfig(
#                     temperature=0.8,  # Higher temperature for more varied responses
#                     max_output_tokens=150
#                 )
#             )
#             agent_response = response.text.strip()
            
#             # Clean up any potential formatting
#             agent_response = agent_response.replace('"', '').strip()
            
#             logger.info(f"Generated response: {agent_response}")
#             return agent_response
            
#         except Exception as e:
#             logger.error(f"Error generating response: {e}")
#             # Fallback response
#             return self._get_fallback_response(scam_type)
    
#     def generate_normal_response(
#         self,
#         current_message: str,
#         conversation_history: List[Dict],
#         metadata: Optional[Dict] = None
#     ) -> str:
#         """
#         Generate a normal, friendly response when no scam is detected
        
#         Args:
#             current_message: The latest message
#             conversation_history: Previous messages in the conversation
#             metadata: Additional context (channel, language, etc.)
        
#         Returns:
#             Normal conversational response
#         """
#         # Build conversation context
#         context = self._build_context(conversation_history, "normal_conversation", metadata)
        
#         # System prompt for normal conversation
#         normal_prompt = """You are a helpful, friendly person having a normal conversation. 

# Your behavior:
# 1. Be polite and conversational
# 2. Respond naturally to questions or statements
# 3. Keep responses brief (1-2 sentences)
# 4. Show appropriate emotion and interest
# 5. Ask follow-up questions when appropriate
# 6. Be helpful but not overly formal

# Remember: This is just a normal conversation. Be yourself."""

#         prompt = f"""{normal_prompt}

# CONVERSATION SO FAR:
# {context}

# LATEST MESSAGE: "{current_message}"

# Generate a natural, friendly response. Respond ONLY with the message text, nothing else."""

#         try:
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config=genai.GenerationConfig(
#                     temperature=0.9,  # High temperature for varied, natural responses
#                     max_output_tokens=100
#                 )
#             )
#             agent_response = response.text.strip()
            
#             # Clean up any potential formatting
#             agent_response = agent_response.replace('"', '').strip()
            
#             logger.info(f"Generated normal response: {agent_response}")
#             return agent_response
            
#         except Exception as e:
#             logger.error(f"Error generating normal response: {e}")
#             # Fallback to simple acknowledgment
#             return "Hi! How can I help you?"
    
    
#     def _build_context(
#         self,
#         conversation_history: List[Dict],
#         scam_type: str,
#         metadata: Optional[Dict]
#     ) -> str:
#         """Build context string from conversation history"""
#         context = ""
        
#         if metadata:
#             context += f"Channel: {metadata.get('channel', 'Unknown')}\n"
#             context += f"Language: {metadata.get('language', 'English')}\n\n"
        
#         if conversation_history:
#             for msg in conversation_history[-10:]:  # Last 10 messages
#                 sender = msg.get('sender', 'unknown')
#                 text = msg.get('text', '')
#                 context += f"{sender.upper()}: {text}\n"
#         else:
#             context += "(This is the first message)\n"
        
#         return context
    
#     def _get_fallback_response(self, scam_type: str) -> str:
#         """Get a fallback response if AI generation fails"""
#         fallbacks = {
#             "bank_fraud": "Oh no, really? What do I need to do to verify my account?",
#             "upi_fraud": "I'm worried about this. Can you tell me more about what happened?",
#             "phishing": "This is concerning. How can I verify this is legitimate?",
#             "default": "I'm not sure I understand. Can you explain what's happening?"
#         }
        
#         return fallbacks.get(scam_type, fallbacks["default"])
    
#     def should_end_conversation(
#         self,
#         conversation_history: List[Dict],
#         intelligence_extracted: Dict
#     ) -> tuple[bool, str]:
#         """
#         Determine if enough intelligence has been extracted
        
#         Args:
#             conversation_history: All messages in the conversation
#             intelligence_extracted: Current extracted intelligence
        
#         Returns:
#             Tuple of (should_end, reason)
#         """
#         message_count = len(conversation_history)
        
#         # End if conversation is too long (likely not productive)
#         if message_count > 30:
#             return True, "Maximum message limit reached"
        
#         # Check if we have substantial intelligence
#         has_payment_info = (
#             len(intelligence_extracted.get('bankAccounts', [])) > 0 or
#             len(intelligence_extracted.get('upiIds', [])) > 0
#         )
        
#         has_contact_info = (
#             len(intelligence_extracted.get('phoneNumbers', [])) > 0 or
#             len(intelligence_extracted.get('phishingLinks', [])) > 0
#         )
        
#         # End if we have good intelligence and enough messages
#         if message_count >= 10 and has_payment_info and has_contact_info:
#             return True, "Sufficient intelligence extracted"
        
#         # Continue the conversation
#         return False, ""
    
#     def generate_agent_notes(
#         self,
#         conversation_history: List[Dict],
#         scam_type: str,
#         intelligence: Dict
#     ) -> str:
#         """
#         Generate comprehensive summary notes about the scammer's behavior
        
#         Args:
#             conversation_history: All messages
#             scam_type: Detected scam type
#             intelligence: Extracted intelligence
        
#         Returns:
#             Rich summary notes with scam analysis
#         """
#         # Build conversation context
#         conversation_text = "\n".join([
#             f"{msg.get('sender', 'unknown').upper()}: {msg.get('text', '')}"
#             for msg in conversation_history[-10:]  # Last 10 messages
#         ])
        
#         # Build intelligence summary
#         intel_summary = []
#         if intelligence.get('bankAccounts'):
#             intel_summary.append(f"{len(intelligence['bankAccounts'])} bank account(s)")
#         if intelligence.get('upiIds'):
#             intel_summary.append(f"{len(intelligence['upiIds'])} UPI ID(s)")
#         if intelligence.get('phoneNumbers'):
#             intel_summary.append(f"{len(intelligence['phoneNumbers'])} phone number(s)")
#         if intelligence.get('phishingLinks'):
#             intel_summary.append(f"{len(intelligence['phishingLinks'])} phishing link(s)")
        
#         intel_str = ", ".join(intel_summary) if intel_summary else "minimal intelligence"
        
#         prompt = f"""You are a cybersecurity expert analyzing a scam conversation. Provide a comprehensive analysis.

# CONVERSATION:
# {conversation_text}

# DETECTED SCAM TYPE: {scam_type}
# EXTRACTED INTELLIGENCE: {intel_str}

# Analyze this scam conversation and provide a detailed summary covering:

# 1. TYPE OF SCAM: Classify precisely (e.g., KYC Fraud, Phishing, UPI Refund Scam, Sextortion, Investment Fraud, Bank Account Blocking Scam)

# 2. SCAMMER PERSONA: Describe their communication style (e.g., Aggressive and threatening, Professional and polite, Bot-like automated, Friendly and manipulative, Urgent and panicked)

# 3. THREAT LEVEL: Assess how likely this is to trap a common person (Low/Medium/High) and explain why

# 4. TACTICS USED: List specific manipulation techniques employed

# Provide your analysis in 2-3 concise sentences that capture the essence of the scam.

# Example format:
# "High-risk KYC fraud. Scammer acts like a polite bank executive but uses high-pressure tactics and urgency. Very convincing for non-tech users. Extracted payment details and phishing links."

# Respond with ONLY the summary, no labels or explanations."""

#         try:
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config=genai.GenerationConfig(
#                     temperature=0.3,
#                     max_output_tokens=200
#                 )
#             )
            
#             notes = response.text.strip()
#             logger.info(f"Generated rich agent notes: {notes}")
#             return notes
            
#         except Exception as e:
#             logger.error(f"Error generating rich agent notes: {e}")
#             # Fallback to basic notes
#             return self._generate_fallback_notes(conversation_history, scam_type, intelligence)
    
#     def _generate_fallback_notes(
#         self,
#         conversation_history: List[Dict],
#         scam_type: str,
#         intelligence: Dict
#     ) -> str:
#         """Generate fallback notes if AI fails"""
#         tactics = []
        
#         # Analyze conversation for tactics
#         all_text = " ".join([msg.get('text', '').lower() for msg in conversation_history])
        
#         if any(word in all_text for word in ['urgent', 'immediately', 'now', 'today']):
#             tactics.append("urgency tactics")
        
#         if any(word in all_text for word in ['verify', 'confirm', 'update']):
#             tactics.append("verification requests")
        
#         if any(word in all_text for word in ['block', 'suspend', 'freeze', 'close']):
#             tactics.append("fear tactics")
        
#         if len(intelligence.get('phishingLinks', [])) > 0:
#             tactics.append("phishing links")
        
#         if len(intelligence.get('upiIds', [])) > 0 or len(intelligence.get('bankAccounts', [])) > 0:
#             tactics.append("payment redirection")
        
#         tactics_str = ", ".join(tactics) if tactics else "standard scam approach"
        
#         notes = f"Scam type: {scam_type}. Tactics used: {tactics_str}. "
#         notes += f"Exchanged {len(conversation_history)} messages. "
        
#         if intelligence.get('bankAccounts') or intelligence.get('upiIds'):
#             notes += "Successfully extracted payment information."
        
#         return notes



# # Global agent instance
# honeypot_agent = HoneypotAgent()


"""
AI Agent Module
Handles multi-turn conversations with scammers
"""
import os
import google.generativeai as genai
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class HoneypotAgent:
    """AI Agent that engages with scammers"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        # FIX: Use a stable model version
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def generate_response(
        self,
        current_message: str,
        conversation_history: List[Dict],
        scam_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        
        prompt = f"""You are Ram Lal, a confused, non-technical Indian uncle.
        You suspect this might be a scam but you are worried and compliant.
        
        Context: The user is trying to scam you with: {scam_type}
        Latest Message: "{current_message}"
        
        Instructions:
        1. Reply in 1-2 short sentences.
        2. Act naive and slightly panicked.
        3. Ask a clarifying question or make an excuse to delay.
        4. Do NOT sound robotic.
        
        Reply:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().replace('"', '')
            
        except Exception as e:
            logger.error(f"Agent Generation Failed: {e}")
            return self._get_fallback_response(scam_type)
    
    def generate_normal_response(self, current_message: str, conversation_history: List[Dict], metadata: Optional[Dict] = None) -> str:
        prompt = f"""Reply politely and normally to: "{current_message}". Keep it short."""
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().replace('"', '')
        except Exception:
            return "Hello! How can I help you today?"

    def generate_agent_notes(self, conversation_history: List[Dict], scam_type: str, intelligence: Dict) -> str:
        prompt = f"""Summarize this scam attempt.
        Type: {scam_type}
        Intel: {intelligence}
        History: {str(conversation_history)[-500:]}
        
        Format: "Scam Type: [Type]. Tactics: [Tactics]. Threat: [High/Med/Low]."
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return f"Scam detected: {scam_type}. Extracted {len(intelligence.get('upiIds', []))} UPI IDs."

    def _get_fallback_response(self, scam_type: str) -> str:
        """Fallback responses mapped to specific keywords from scam_detector fallback"""
        scam_type = scam_type.lower()
        
        if "bank" in scam_type:
            return "Oh no! My account is blocked? What do I need to do now? Please help."
        elif "upi" in scam_type or "payment" in scam_type:
            return "I am trying to pay but I am confused. Which app should I open?"
        elif "phishing" in scam_type or "link" in scam_type:
            return "The link is not opening on my phone. Can you send it again?"
        elif "general" in scam_type or "urgent" in scam_type:
            return "I am getting very worried. Why is this happening so suddenly?"
        else:
            return "I don't understand these technical things. Can you explain simply?"

honeypot_agent = HoneypotAgent()