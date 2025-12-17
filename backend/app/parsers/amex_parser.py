import re
from app.parsers.base_parser import BaseParser

class AmexParser(BaseParser):
    """American Express-specific parser"""
    
    def extract_with_regex(self, text: str) -> dict:
        """Extract using Amex-specific patterns"""
        result = {}
        
        # Issuer
        result["issuer"] = {
            "value": "American Express",
            "method": "regex"
        }
        
        # Card last 4 - Amex uses different masking (often shows last 5)
        card_patterns = [
            r"Card (?:Ending|ending|Number)[:\s]*(?:\*+|X+|x+)\s*(\d{4,5})",
            r"(?:Account|Card) No\.[:\s]*(?:\*+|X+)\s*(\d{4,5})",
            r"Card Member\s*(?:No\.|Number)[:\s]*(?:\*+|X+)\s*(\d{4,5})",
            r"(\d{5})\s*\(last (?:five|5) digits\)"
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get last 4 digits if 5 are captured
                digits = match.group(1)
                result["card_last_4"] = {
                    "value": digits[-4:],
                    "method": "regex"
                }
                break
        
        # Statement period - Amex formats
        period_patterns = [
            r"Statement (?:Period|Date)[:\s]*([A-Z][a-z]{2}\s+\d{1,2},\s*\d{4})\s*-\s*([A-Z][a-z]{2}\s+\d{1,2},\s*\d{4})",
            r"Billing Period[:\s]*(\d{1,2}/\d{1,2}/\d{4})\s*(?:through|to|-)\s*(\d{1,2}/\d{1,2}/\d{4})",
            r"Statement Closing Date[:\s]*([^\n]{10,30})"
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
        
        # Due date - Amex specific wording
        due_patterns = [
            r"Payment Due Date[:\s]*([A-Z][a-z]{2}\s+\d{1,2},\s*\d{4})",
            r"Please Pay By[:\s]*(\d{1,2}/\d{1,2}/\d{4})",
            r"(?:Due Date|Pay by)[:\s]*([^\n]{8,25})"
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["due_date"] = {
                    "value": match.group(1).strip(),
                    "method": "regex"
                }
                break
        
        # Total amount due - Amex often uses "New Balance" or "Total Due"
        amount_patterns = [
            r"New Balance[:\s]*(?:\$|₹|Rs\.?)?\s*([\d,]+\.?\d*)",
            r"Total (?:Amount )?Due[:\s]*(?:\$|₹|Rs\.?)?\s*([\d,]+\.?\d*)",
            r"Payment Amount[:\s]*(?:\$|₹|Rs\.?)?\s*([\d,]+\.?\d*)",
            r"Closing Balance[:\s]*(?:\$|₹|Rs\.?)?\s*([\d,]+\.?\d*)"
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