import re
from app.parsers.base_parser import BaseParser

class HDFCParser(BaseParser):
    """HDFC-specific parser with multiple extraction strategies"""
    
    def extract_with_regex(self, text: str) -> dict:
        """Extract using HDFC-specific patterns"""
        result = {}
        
        # Issuer
        result["issuer"] = {
            "value": "HDFC Bank",
            "method": "regex"
        }
        
        # Card last 4 - try multiple patterns
        card_patterns = [
            r"(?:Card Number|Credit Card No\.?)\s*[:\-]?\s*(?:XXXX\s*){3}(\d{4})",
            r"XXXX\s*XXXX\s*XXXX\s*(\d{4})",
            r"ending\s+(?:in\s+)?(\d{4})"
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["card_last_4"] = {
                    "value": match.group(1),
                    "method": "regex"
                }
                break
        
        # Statement period
        period_patterns = [
            r"Statement (?:Period|Date)[:\-\s]+([^\n]+)",
            r"(?:From|Period)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(?:to|To)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ]
        
        for pattern in period_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.lastindex == 2:
                    result["statement_period"] = {
                        "value": f"{match.group(1)} to {match.group(2)}",
                        "method": "regex"
                    }
                else:
                    result["statement_period"] = {
                        "value": match.group(1).strip(),
                        "method": "regex"
                    }
                break
        
        # Due date
        due_patterns = [
            r"Payment (?:Due Date|Due By)[:\-\s]+(\d{1,2}[/-][A-Za-z]{3}[/-]\d{2,4})",
            r"(?:Due Date|Pay By)[:\-\s]+([^\n]{5,20})"
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["due_date"] = {
                    "value": match.group(1).strip(),
                    "method": "regex"
                }
                break
        
        # Total amount due
        amount_patterns = [
            r"Total (?:Amount )?Due[:\-\s]+(?:Rs\.?|₹)\s*([\d,]+\.?\d*)",
            r"(?:Amount Due|Total Outstanding)[:\-\s]+(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)"
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["total_amount_due"] = {
                    "value": match.group(1).replace(",", ""),
                    "method": "regex"
                }
                break
        
        return result