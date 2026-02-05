"""
Image Generator Module
Generates realistic fake documents using Google Gemini Imagen
"""
import os
import google.generativeai as genai
from typing import Optional
import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates images for scammer requests using Google Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Create directory for generated images
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_cancelled_check(self, account_holder: str = "John Doe") -> Optional[str]:
        """
        Generate a cancelled check image
        
        Args:
            account_holder: Name to put on the check
        
        Returns:
            Base64 encoded image string or None if generation fails
        """
        prompt = f"""Generate a realistic cancelled check image with the following details:
- Account holder name: {account_holder}
- Bank name: Generic Bank
- Check number: Random 4-digit number
- Account number: Partially visible (XXXX-XXXX-1234)
- Routing number: Partially visible
- Large "CANCELLED" or "VOID" stamp diagonally across the check
- Professional banking check design
- Slightly aged/used appearance

Make it look authentic but clearly marked as cancelled."""

        try:
            # Note: Gemini 2.0 Flash doesn't have native image generation
            # We'll use a text-based approach to inform the agent
            logger.info("Image generation requested for cancelled check")
            
            # For now, return a placeholder message
            # In production, you would integrate with Imagen API or similar
            return self._generate_placeholder_response("cancelled check")
            
        except Exception as e:
            logger.error(f"Error generating cancelled check: {e}")
            return None
    
    def generate_id_document(self, name: str = "John Doe") -> Optional[str]:
        """
        Generate a fake ID document image
        
        Args:
            name: Name to put on the ID
        
        Returns:
            Base64 encoded image string or None if generation fails
        """
        prompt = f"""Generate a generic ID card image with:
- Name: {name}
- Photo: Generic silhouette
- ID number: Random alphanumeric
- Issue date: Recent date
- Expiry date: Future date
- Watermark or security features
- Professional government ID appearance

Make it look generic and not tied to any real government."""

        try:
            logger.info("Image generation requested for ID document")
            return self._generate_placeholder_response("ID document")
            
        except Exception as e:
            logger.error(f"Error generating ID document: {e}")
            return None
    
    def generate_payment_screenshot(self, amount: str = "1000", upi_id: str = "user@upi") -> Optional[str]:
        """
        Generate a fake payment screenshot
        
        Args:
            amount: Payment amount
            upi_id: UPI ID for the payment
        
        Returns:
            Base64 encoded image string or None if generation fails
        """
        prompt = f"""Generate a mobile payment app screenshot showing:
- Payment amount: ₹{amount}
- Recipient UPI ID: {upi_id}
- Transaction status: Pending or Processing
- Transaction ID: Random alphanumeric
- Timestamp: Recent time
- Generic payment app interface (not specific to any real app)
- Mobile phone screen appearance

Make it look like a legitimate payment app screenshot."""

        try:
            logger.info("Image generation requested for payment screenshot")
            return self._generate_placeholder_response("payment screenshot")
            
        except Exception as e:
            logger.error(f"Error generating payment screenshot: {e}")
            return None
    
    def _generate_placeholder_response(self, doc_type: str) -> str:
        """
        Generate a text response indicating the document is being prepared
        
        Args:
            doc_type: Type of document requested
        
        Returns:
            Message to send to scammer
        """
        responses = {
            "cancelled check": "I'm preparing the cancelled check image. It will take a moment to scan it. Can you tell me where exactly I should send this?",
            "ID document": "I'm getting my ID ready to photograph. Before I share it, can you confirm this is really from my bank? What's your employee ID?",
            "payment screenshot": "I'm opening my payment app now. Just to be safe, can you confirm the exact amount I should send and your official UPI ID?"
        }
        
        return responses.get(doc_type, "I'm preparing that document. Just give me a moment.")
    
    def should_generate_image(self, message: str) -> tuple[bool, str]:
        """
        Determine if the scammer is requesting an image
        
        Args:
            message: The scammer's message
        
        Returns:
            Tuple of (should_generate, image_type)
        """
        message_lower = message.lower()
        
        # Check for various image requests
        if any(word in message_lower for word in ['check', 'cheque', 'cancelled check']):
            return True, "cancelled_check"
        
        if any(word in message_lower for word in ['id card', 'id proof', 'identity', 'aadhar', 'pan card', 'license']):
            return True, "id_document"
        
        if any(word in message_lower for word in ['screenshot', 'payment proof', 'transaction', 'receipt']):
            return True, "payment_screenshot"
        
        if any(word in message_lower for word in ['photo', 'picture', 'image', 'scan']):
            return True, "generic_document"
        
        return False, ""


# Global image generator instance
image_generator = ImageGenerator()
