import re
from typing import Optional, Tuple
import structlog

logger = structlog.get_logger()

class IssuerDetector:
    """Multi-strategy issuer detection"""
    
    ISSUER_PATTERNS = {
        "HDFC": [r"hdfc\s+bank", r"hdfc\s+credit\s+card"],
        "ICICI": [r"icici\s+bank", r"icici\s+credit"],
        "SBI": [r"sbi\s+card", r"state\s+bank.*card"],
        "AXIS": [r"axis\s+bank", r"axis\s+credit"],
        "AMEX": [r"american\s+express", r"amex"]
    }
    
    @classmethod
    def detect(cls, text: str) -> Tuple[Optional[str], float]:
        """
        Detect issuer with confidence score
        Returns: (issuer_name, confidence)
        """
        text_lower = text.lower()
        scores = {}
        
        for issuer, patterns in cls.ISSUER_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            
            if score > 0:
                scores[issuer] = score
        
        if not scores:
            logger.warning("issuer_not_detected")
            return None, 0.0
        
        # Get issuer with highest score
        detected_issuer = max(scores, key=scores.get)

        # Calculate confidence normalized by the number of patterns defined for that issuer
        max_possible = len(cls.ISSUER_PATTERNS.get(detected_issuer, [])) or 1
        confidence = min(scores[detected_issuer] / float(max_possible), 1.0)
        
        logger.info("issuer_detected", issuer=detected_issuer, confidence=confidence)
        return detected_issuer, confidence