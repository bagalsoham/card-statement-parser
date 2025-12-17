import re
from app.parsers.base_parser import BaseParser

class SBIParser(BaseParser):
    """SBI Card-specific parser"""
    
    def extract_with_regex(self, text: str) -> dict:
        """Extract using SBI Card-specific patterns"""
        result = {}
        
        # Issuer
        result["issuer"] = {
            "value": "SBI Card",
            "method": "regex"
        }
        
        # Card last 4 - SBI Card formats
        card_patterns = [
            r"Card No\.?\s*[:\-]?\s*(?:XXXX\s*){3}(\d{4})",
            r"(?:Card ending with|ending in)\s*(\d{4})",
            r"xxxx\s*xxxx\s*xxxx\s*(\d{4})",
            r"Primary Card[:\s]*\*+\s*(\d{4})"
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["card_last_4"] = {
                    "value": match.group(1),
                    "method": "regex"
                }
                break
        
        # Statement period - SBI uses DD/MM/YYYY format
        period_patterns = [
            r"Statement Period[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            r"Billing (?:Cycle|Period)[:\s]*([^\n]{15,50})",
            r"From\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*To\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})"
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
            r"Payment Due Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            r"(?:Pay by|Due on)[:\s]*(\d{1,2}\s+[A-Za-z]{3,9},?\s+\d{4})",
            r"Last (?:Date|Day) (?:of|for) Payment[:\s]*([^\n]{8,25})"
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["due_date"] = {
                    "value": match.group(1).strip(),
                    "method": "regex"
                }
                break
        
        # Total amount due - SBI formats
        amount_patterns = [
            r"Total Amount Due[:\s]*Rs\.?\s*([\d,]+\.?\d*)",
            r"(?:Current|Total) (?:Dues|Outstanding)[:\s]*(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)",
            r"Minimum Amount Due[:\s]*(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)"
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