import re
from app.parsers.base_parser import BaseParser

class ICICIParser(BaseParser):
    """ICICI Bank-specific parser"""
    
    def extract_with_regex(self, text: str) -> dict:
        """Extract using ICICI-specific patterns"""
        result = {}
        
        # Issuer
        result["issuer"] = {
            "value": "ICICI Bank",
            "method": "regex"
        }
        
        # Card last 4 - ICICI often uses different formats
        card_patterns = [
            r"Card (?:No\.|Number)[:\s]*(?:XX+|\*+)\s*(\d{4})",
            r"(?:ending|Ending) (?:with|in)\s*(\d{4})",
            r"Card[:\s]*\*+\s*(\d{4})",
            r"(\d{4})\s*(?:is your card number|card)"
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["card_last_4"] = {
                    "value": match.group(1),
                    "method": "regex"
                }
                break
        
        # Statement period - ICICI uses "Statement From...To" format
        period_patterns = [
            r"Statement (?:from|From)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|To)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"Billing Period[:\s]*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s*to\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})",
            r"Statement Period[:\s]*([^\n]{10,40})"
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
        
        # Due date - ICICI common formats
        due_patterns = [
            r"Payment Due (?:Date|By)[:\s]*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
            r"(?:Due Date|Pay by)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"Last Date (?:of|for) Payment[:\s]*([^\n]{8,25})"
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["due_date"] = {
                    "value": match.group(1).strip(),
                    "method": "regex"
                }
                break
        
        # Total amount due - ICICI formats
        amount_patterns = [
            r"Total (?:Amount )?Due[:\s]*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)",
            r"Minimum (?:Amount )?Due[:\s]*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)",
            r"(?:Outstanding|Current) (?:Balance|Amount)[:\s]*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)"
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