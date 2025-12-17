import re
from datetime import datetime
from typing import Tuple
import structlog

logger = structlog.get_logger()

class FieldValidator:
    """Validation and confidence scoring for extracted fields"""
    
    @staticmethod
    def validate_card_last_4(value: str) -> Tuple[bool, float]:
        """Validate card last 4 digits"""
        if not value:
            return False, 0.0
        
        # Remove spaces and special chars
        cleaned = re.sub(r'[^\d]', '', value)
        
        if len(cleaned) == 4 and cleaned.isdigit():
            return True, 1.0
        elif len(cleaned) > 4:
            # Try to extract last 4
            return True, 0.8
        
        return False, 0.0
    
    @staticmethod
    def validate_date(value: str) -> Tuple[bool, float]:
        """Validate date format"""
        if not value:
            return False, 0.0
        
        # Common date formats
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}',
            r'[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, value):
                return True, 0.9
        
        return False, 0.3
    
    @staticmethod
    def validate_amount(value: str) -> Tuple[bool, float]:
        """Validate monetary amount"""
        if not value:
            return False, 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[₹$,\s]', '', value)
        
        # Check if it's a valid number
        try:
            amount = float(cleaned)
            if amount >= 0:
                return True, 1.0
            return False, 0.5
        except ValueError:
            return False, 0.0
    
    @staticmethod
    def validate_issuer(value: str) -> Tuple[bool, float]:
        """Validate issuer name"""
        if not value:
            return False, 0.0
        
        known_issuers = ["HDFC", "ICICI", "SBI", "AXIS", "AMEX", 
                        "hdfc", "icici", "sbi", "axis", "amex"]
        
        for issuer in known_issuers:
            if issuer.lower() in value.lower():
                return True, 1.0
        
        # Has some text
        if len(value) > 2:
            return True, 0.5
        
        return False, 0.0