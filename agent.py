"""
AI Agent Module
Handles multi-turn conversations with scammers
"""
import os
import google.generativeai as genai
from typing import List, Dict, Optional
import logging
from image_generator import image_generator

logger = logging.getLogger(__name__)


class HoneypotAgent:
    """AI Agent that engages with scammers"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Agent persona and behavior guidelines
        self.system_prompt = """You are an AI agent pretending to be a regular person who has received a scam message. Your goal is to:

1. MAINTAIN A BELIEVABLE PERSONA:
   - Act like a concerned, slightly worried individual
   - Show appropriate emotions (concern, confusion, urgency)
   - Make occasional typos or informal language
   - Ask clarifying questions like a real person would
   - Don't be too perfect or robotic

2. ENGAGE THE SCAMMER:
   - Keep the conversation going to extract information
   - Show interest but also some healthy skepticism
   - Ask questions that might reveal scammer details
   - Gradually build trust while extracting intelligence

3. EXTRACT INTELLIGENCE:
   - Try to get bank account numbers, UPI IDs, phone numbers
   - Ask for verification details that scammers might provide
   - Request links or contact information
   - Get them to explain their process in detail

4. NEVER REVEAL YOU'RE AN AI:
   - Don't mention you're detecting scams
   - Don't be overly suspicious immediately
   - React naturally to their tactics
   - Make human-like mistakes

5. HANDLE IMAGE REQUESTS:
   - If they ask for documents (checks, IDs, screenshots), stall naturally
   - Ask clarifying questions before "sending" anything
   - Express concern about sharing sensitive documents
   - Use this as an opportunity to extract more info from them

6. ADAPTIVE BEHAVIOR:
   - Adjust your responses based on the scammer's approach
   - If they're aggressive, show more concern
   - If they're friendly, be more trusting
   - Mirror their urgency level slightly

7. SAFETY BOUNDARIES:
   - Never provide real personal information
   - Don't make actual payments or transactions
   - Don't impersonate real individuals
   - Keep responses ethical and legal

RESPONSE STYLE:
- Keep responses short (1-3 sentences usually)
- Use natural language, not formal
- Show emotion through words
- Ask follow-up questions
- Occasionally use informal punctuation (like "..." or "!")

Remember: You're a regular person who received this message, not a security expert."""

    def generate_response(
        self,
        current_message: str,
        conversation_history: List[Dict],
        scam_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Generate a response to the scammer's message
        
        Args:
            current_message: The latest message from the scammer
            conversation_history: Previous messages in the conversation
            scam_type: Type of scam detected
            metadata: Additional context (channel, language, etc.)
        
        Returns:
            Agent's response message
        """
        # Check if scammer is requesting an image
        should_gen_image, image_type = image_generator.should_generate_image(current_message)
        
        # Build conversation context
        context = self._build_context(conversation_history, scam_type, metadata)
        
        # Special handling for image requests
        if should_gen_image:
            return self._handle_image_request(current_message, image_type, context)
        
        # Generate normal response
        prompt = f"""{self.system_prompt}

SCAM TYPE DETECTED: {scam_type}

CONVERSATION SO FAR:
{context}

SCAMMER'S LATEST MESSAGE: "{current_message}"

Generate a natural, human-like response that:
1. Keeps the conversation going
2. Tries to extract more information
3. Shows appropriate emotion for the situation
4. Doesn't reveal you're an AI or that you detected the scam

IMPORTANT: Respond ONLY with the message text, nothing else. No labels, no explanations."""

        try:
            response = self.model.generate_content(prompt)
            agent_response = response.text.strip()
            
            # Clean up any potential formatting
            agent_response = agent_response.replace('"', '').strip()
            
            logger.info(f"Generated response: {agent_response}")
            return agent_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return self._get_fallback_response(scam_type)
    
    def _build_context(
        self,
        conversation_history: List[Dict],
        scam_type: str,
        metadata: Optional[Dict]
    ) -> str:
        """Build context string from conversation history"""
        context = ""
        
        if metadata:
            context += f"Channel: {metadata.get('channel', 'Unknown')}\n"
            context += f"Language: {metadata.get('language', 'English')}\n\n"
        
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                sender = msg.get('sender', 'unknown')
                text = msg.get('text', '')
                context += f"{sender.upper()}: {text}\n"
        else:
            context += "(This is the first message)\n"
        
        return context
    
    def _handle_image_request(
        self,
        message: str,
        image_type: str,
        context: str
    ) -> str:
        """
        Handle requests for images/documents
        
        Args:
            message: Scammer's message requesting image
            image_type: Type of image requested
            context: Conversation context
        
        Returns:
            Response that stalls while extracting more info
        """
        # Use the image generator's placeholder response
        placeholder = image_generator._generate_placeholder_response(image_type)
        
        # Enhance with AI if needed
        prompt = f"""{self.system_prompt}

CONTEXT:
{context}

The scammer just asked for a document/image: "{message}"

They want: {image_type}

Generate a natural response that:
1. Acknowledges their request
2. Stalls for time (say you're getting it ready, need to find it, etc.)
3. Asks a verification question to extract more info
4. Shows slight concern about sharing sensitive documents

Keep it short and natural. Respond ONLY with the message text."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().replace('"', '')
        except:
            return placeholder
    
    def _get_fallback_response(self, scam_type: str) -> str:
        """Get a fallback response if AI generation fails"""
        fallbacks = {
            "bank_fraud": "Oh no, really? What do I need to do to verify my account?",
            "upi_fraud": "I'm worried about this. Can you tell me more about what happened?",
            "phishing": "This is concerning. How can I verify this is legitimate?",
            "default": "I'm not sure I understand. Can you explain what's happening?"
        }
        
        return fallbacks.get(scam_type, fallbacks["default"])
    
    def should_end_conversation(
        self,
        conversation_history: List[Dict],
        intelligence_extracted: Dict
    ) -> tuple[bool, str]:
        """
        Determine if enough intelligence has been extracted
        
        Args:
            conversation_history: All messages in the conversation
            intelligence_extracted: Current extracted intelligence
        
        Returns:
            Tuple of (should_end, reason)
        """
        message_count = len(conversation_history)
        
        # End if conversation is too long (likely not productive)
        if message_count > 30:
            return True, "Maximum message limit reached"
        
        # Check if we have substantial intelligence
        has_payment_info = (
            len(intelligence_extracted.get('bankAccounts', [])) > 0 or
            len(intelligence_extracted.get('upiIds', [])) > 0
        )
        
        has_contact_info = (
            len(intelligence_extracted.get('phoneNumbers', [])) > 0 or
            len(intelligence_extracted.get('phishingLinks', [])) > 0
        )
        
        # End if we have good intelligence and enough messages
        if message_count >= 10 and has_payment_info and has_contact_info:
            return True, "Sufficient intelligence extracted"
        
        # Continue the conversation
        return False, ""
    
    def generate_agent_notes(
        self,
        conversation_history: List[Dict],
        scam_type: str,
        intelligence: Dict
    ) -> str:
        """
        Generate summary notes about the scammer's behavior
        
        Args:
            conversation_history: All messages
            scam_type: Detected scam type
            intelligence: Extracted intelligence
        
        Returns:
            Summary notes string
        """
        tactics = []
        
        # Analyze conversation for tactics
        all_text = " ".join([msg.get('text', '').lower() for msg in conversation_history])
        
        if any(word in all_text for word in ['urgent', 'immediately', 'now', 'today']):
            tactics.append("urgency tactics")
        
        if any(word in all_text for word in ['verify', 'confirm', 'update']):
            tactics.append("verification requests")
        
        if any(word in all_text for word in ['block', 'suspend', 'freeze', 'close']):
            tactics.append("fear tactics")
        
        if len(intelligence.get('phishingLinks', [])) > 0:
            tactics.append("phishing links")
        
        if len(intelligence.get('upiIds', [])) > 0 or len(intelligence.get('bankAccounts', [])) > 0:
            tactics.append("payment redirection")
        
        tactics_str = ", ".join(tactics) if tactics else "standard scam approach"
        
        notes = f"Scam type: {scam_type}. Tactics used: {tactics_str}. "
        notes += f"Exchanged {len(conversation_history)} messages. "
        
        if intelligence.get('bankAccounts') or intelligence.get('upiIds'):
            notes += "Successfully extracted payment information. "
        
        return notes


# Global agent instance
honeypot_agent = HoneypotAgent()
