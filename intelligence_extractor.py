"""
Intelligence Extractor Module
Extracts scam-related intelligence from conversations
"""
import re
from typing import List
import logging

logger = logging.getLogger(__name__)


class IntelligenceExtractor:
    """Extracts intelligence from scam conversations"""
    
    # Regex patterns for extraction
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'  # 9-18 digit account numbers
    UPI_ID_PATTERN = r'\b[\w\.-]+@[\w\.-]+\b'  # UPI format: name@bank
    PHONE_PATTERN = r'\+?\d{10,15}\b'  # Phone numbers
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'  # URLs
    
    # Suspicious keywords
    SUSPICIOUS_KEYWORDS = [
        'urgent', 'immediately', 'verify', 'blocked', 'suspended',
        'account', 'bank', 'upi', 'payment', 'refund', 'otp', 'pin',
        'cvv', 'card', 'expire', 'update', 'confirm', 'click', 'link',
        'prize', 'won', 'lottery', 'claim', 'reward', 'offer',
        'limited time', 'act now', 'verify now', 'update now',
        'customer care', 'helpline', 'support team', 'security alert'
    ]
    
    def extract_bank_accounts(self, text: str) -> List[str]:
        """Extract bank account numbers from text"""
        accounts = re.findall(self.BANK_ACCOUNT_PATTERN, text)
        # Filter out common false positives (like phone numbers that are too short)
        return [acc for acc in accounts if len(acc) >= 10]
    
    def extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs from text"""
        potential_upis = re.findall(self.UPI_ID_PATTERN, text)
        # Filter to only include common UPI providers
        upi_providers = ['paytm', 'phonepe', 'gpay', 'googlepay', 'ybl', 'okhdfcbank', 
                        'okicici', 'okaxis', 'oksbi', 'airtel', 'freecharge', 'mobikwik']
        
        upis = []
        for upi in potential_upis:
            # Check if it's a valid UPI (has @ and known provider)
            if '@' in upi:
                provider = upi.split('@')[1].lower()
                if any(p in provider for p in upi_providers):
                    upis.append(upi)
        
        return upis
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phones = re.findall(self.PHONE_PATTERN, text)
        # Filter to reasonable phone number lengths
        return [p for p in phones if 10 <= len(p.replace('+', '')) <= 15]
    
    def extract_phishing_links(self, text: str) -> List[str]:
        """Extract URLs from text"""
        return re.findall(self.URL_PATTERN, text)
    
    def extract_suspicious_keywords(self, text: str) -> List[str]:
        """Extract suspicious keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # Remove duplicates
    
    def extract_all(self, messages: List[dict]) -> dict:
        """
        Extract all intelligence from a list of messages
        
        Args:
            messages: List of message dictionaries with 'sender' and 'text' keys
        
        Returns:
            Dictionary with all extracted intelligence
        """
        all_text = " ".join([msg.get('text', '') for msg in messages])
        
        intelligence = {
            'bankAccounts': self.extract_bank_accounts(all_text),
            'upiIds': self.extract_upi_ids(all_text),
            'phishingLinks': self.extract_phishing_links(all_text),
            'phoneNumbers': self.extract_phone_numbers(all_text),
            'suspiciousKeywords': self.extract_suspicious_keywords(all_text)
        }
        
        # Remove duplicates
        for key in intelligence:
            intelligence[key] = list(set(intelligence[key]))
        
        logger.info(f"Extracted intelligence: {intelligence}")
        return intelligence
    
    def update_intelligence(self, existing: dict, new_message: str) -> dict:
        """
        Update existing intelligence with new message
        
        Args:
            existing: Existing intelligence dictionary
            new_message: New message text to extract from
        
        Returns:
            Updated intelligence dictionary
        """
        new_intel = {
            'bankAccounts': self.extract_bank_accounts(new_message),
            'upiIds': self.extract_upi_ids(new_message),
            'phishingLinks': self.extract_phishing_links(new_message),
            'phoneNumbers': self.extract_phone_numbers(new_message),
            'suspiciousKeywords': self.extract_suspicious_keywords(new_message)
        }
        
        # Merge with existing
        for key in existing:
            if key in new_intel:
                existing[key] = list(set(existing[key] + new_intel[key]))
        
        return existing


# Global extractor instance
intelligence_extractor = IntelligenceExtractor()
