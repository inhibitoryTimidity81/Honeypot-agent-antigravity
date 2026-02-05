"""
Hybrid Intelligence Extractor Module
Combines AI-based extraction with regex fallback for maximum reliability
"""
import os
import re
import google.generativeai as genai
from typing import Dict, List
import logging
import json

logger = logging.getLogger(__name__)


class HybridIntelligenceExtractor:
    """Extracts intelligence using AI first, with regex fallback"""
    
    # Regex patterns for fallback extraction
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'  # 9-18 digit account numbers
    UPI_ID_PATTERN = r'\b[\w\.-]+@[\w\.-]+\b'  # UPI format: name@bank
    PHONE_PATTERN = r'(?:\+91|91)?[\s-]?\d{10}\b'  # Indian phone numbers
    URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+'  # URLs
    
    # Suspicious keywords
    SUSPICIOUS_KEYWORDS = [
        'urgent', 'immediately', 'verify', 'blocked', 'suspended',
        'account', 'bank', 'upi', 'payment', 'refund', 'otp', 'pin',
        'cvv', 'card', 'expire', 'update', 'confirm', 'click', 'link',
        'prize', 'won', 'lottery', 'claim', 'reward', 'offer',
        'limited time', 'act now', 'verify now', 'update now',
        'customer care', 'helpline', 'support team', 'security alert',
        'kyc', 'aadhar', 'pan', 'debit', 'credit'
    ]
    
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        # Get model name from environment or use default
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized HybridIntelligenceExtractor with model: {model_name}")
    
    def extract_intelligence_hybrid(self, text: str) -> Dict[str, List[str]]:
        """
        Extract intelligence using AI first, fallback to regex on failure
        
        Args:
            text: Text to extract intelligence from
        
        Returns:
            Dictionary with extracted intelligence:
            {
                'bankAccounts': [],
                'upiIds': [],
                'phishingLinks': [],
                'phoneNumbers': [],
                'suspiciousKeywords': []
            }
        """
        logger.info("Starting hybrid intelligence extraction")
        
        # Try AI extraction first
        ai_result = self._extract_with_ai(text)
        
        # If AI succeeded, use AI results only
        if ai_result:
            logger.info("Using AI extraction results")
            return ai_result
        
        # If AI failed, fall back to regex
        logger.warning("AI extraction failed, falling back to regex")
        regex_result = self._extract_with_regex(text)
        
        logger.info(f"Extracted intelligence: {regex_result}")
        return regex_result
    
    def _extract_with_ai(self, text: str) -> Dict[str, List[str]]:
        """
        Extract intelligence using Gemini AI
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with extracted data or empty dict on failure
        """
        prompt = f"""You are an expert at analyzing scam messages and extracting actionable intelligence.

Analyze the following text and extract ALL instances of:
1. Bank Account Numbers (9-18 digits)
2. UPI IDs (format: name@bank)
3. Phishing Links (any URLs)
4. Phone Numbers (Indian format, with or without +91)
5. Suspicious Keywords (words that indicate scam tactics)

Text to analyze:
"{text}"

Return ONLY a valid JSON object with this EXACT structure (no markdown, no explanation):
{{
  "bankAccounts": [],
  "upiIds": [],
  "phishingLinks": [],
  "phoneNumbers": [],
  "suspiciousKeywords": []
}}

If you find nothing for a category, return an empty array. Extract ALL instances you find."""

        try:
            logger.info("Attempting AI-based extraction")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000
                )
            )
            
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            # Parse JSON
            result = json.loads(result_text)
            
            # Validate structure
            required_keys = ['bankAccounts', 'upiIds', 'phishingLinks', 'phoneNumbers', 'suspiciousKeywords']
            if all(key in result for key in required_keys):
                logger.info("AI extraction successful")
                return result
            else:
                logger.warning("AI extraction returned incomplete data")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"AI extraction failed - invalid JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return {}
    
    def _extract_with_regex(self, text: str) -> Dict[str, List[str]]:
        """
        Extract intelligence using regex patterns (fallback method)
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with extracted data
        """
        logger.info("Running regex extraction")
        
        result = {
            'bankAccounts': self._extract_bank_accounts(text),
            'upiIds': self._extract_upi_ids(text),
            'phishingLinks': self._extract_urls(text),
            'phoneNumbers': self._extract_phone_numbers(text),
            'suspiciousKeywords': self._extract_keywords(text)
        }
        
        return result
    
    def _extract_bank_accounts(self, text: str) -> List[str]:
        """Extract bank account numbers"""
        accounts = re.findall(self.BANK_ACCOUNT_PATTERN, text)
        # Filter out phone numbers (10 digits) and keep only 11+ digits
        return list(set([acc for acc in accounts if len(acc) >= 11]))
    
    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs"""
        potential_upis = re.findall(self.UPI_ID_PATTERN, text)
        
        # Filter to only include common UPI providers
        upi_providers = [
            'paytm', 'phonepe', 'gpay', 'googlepay', 'ybl', 'okhdfcbank',
            'okicici', 'okaxis', 'oksbi', 'airtel', 'freecharge', 'mobikwik',
            'ibl', 'axl', 'upi'
        ]
        
        upis = []
        for upi in potential_upis:
            if '@' in upi:
                provider = upi.split('@')[1].lower()
                if any(p in provider for p in upi_providers):
                    upis.append(upi)
        
        return list(set(upis))
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers"""
        phones = re.findall(self.PHONE_PATTERN, text)
        
        # Clean and normalize
        cleaned_phones = []
        for phone in phones:
            # Remove spaces and hyphens
            phone = phone.replace(' ', '').replace('-', '')
            # Remove +91 or 91 prefix for consistency
            if phone.startswith('+91'):
                phone = phone[3:]
            elif phone.startswith('91') and len(phone) == 12:
                phone = phone[2:]
            
            # Only keep 10-digit numbers
            if len(phone) == 10 and phone.isdigit():
                cleaned_phones.append(phone)
        
        return list(set(cleaned_phones))
    
    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs"""
        urls = re.findall(self.URL_PATTERN, text)
        return list(set(urls))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract suspicious keywords"""
        text_lower = text.lower()
        found_keywords = []
        
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))
    
    def _merge_results(self, ai_result: Dict, regex_result: Dict) -> Dict[str, List[str]]:
        """
        Merge AI and regex results, removing duplicates
        
        Args:
            ai_result: Results from AI extraction
            regex_result: Results from regex extraction
        
        Returns:
            Merged results
        """
        merged = {
            'bankAccounts': [],
            'upiIds': [],
            'phishingLinks': [],
            'phoneNumbers': [],
            'suspiciousKeywords': []
        }
        
        # If AI failed, use regex only
        if not ai_result:
            logger.info("Using regex results only (AI failed)")
            return regex_result
        
        # Merge each category
        for key in merged.keys():
            ai_items = ai_result.get(key, [])
            regex_items = regex_result.get(key, [])
            
            # Combine and remove duplicates
            combined = list(set(ai_items + regex_items))
            merged[key] = combined
        
        logger.info(f"Merged {len(merged['bankAccounts'])} bank accounts, "
                   f"{len(merged['upiIds'])} UPI IDs, "
                   f"{len(merged['phishingLinks'])} links, "
                   f"{len(merged['phoneNumbers'])} phone numbers, "
                   f"{len(merged['suspiciousKeywords'])} keywords")
        
        return merged


# Global instance
hybrid_extractor = HybridIntelligenceExtractor()
