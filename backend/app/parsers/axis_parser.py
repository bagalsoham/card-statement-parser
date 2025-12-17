import re
from app.parsers.base_parser import BaseParser

class AxisParser(BaseParser):
    """Axis Bank-specific parser"""
    
    def extract_with_regex(self, text: str) -> dict:
        """Extract using Axis Bank-specific patterns"""
        result = {}
        
        # Issuer
        result["issuer"] = {
            "value": "Axis Bank",
            "method": "regex"
        }
        
        # Card last 4 - Axis formats
        card_patterns = [
            r"Card Number[:\s]*(?:XX+|\*+)\s*(\d{4})",
            r"(?:ending with|last four digits)[:\s]*(\d{4})",
            r"Primary Card No\.[:\s]*\*+\s*(\d{4})",
            r"(?:Card|A/c) (?:No\.|Number)[:\s]*X+\s*(\d{4})"
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["card_last_4"] = {
                    "value": match.group(1),
                    "method": "regex"
                }
                break
        
        # Statement period - Axis uses various formats
        period_patterns = [
            r"Statement (?:Date|Period)[:\s]*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s*to\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})",
            r"Billing (?:Cycle|Period)[:\s]*([^\n]{12,45})",
            r"From[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*To[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})"
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
        
        # Due date - Axis formats
        due_patterns = [
            r"Payment Due Date[:\s]*(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
            r"(?:Due Date|Pay By)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
            r"Last Date to Pay[:\s]*([^\n]{8,25})"
        ]
        
        for pattern in due_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["due_date"] = {
                    "value": match.group(1).strip(),
                    "method": "regex"
                }
                break
        
        # Total amount due - Axis formats
        amount_patterns = [
            r"Total Amount Due[:\s]*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)",
            r"Current (?:Outstanding|Dues)[:\s]*(?:Rs\.?|₹|INR)?\s*([\d,]+\.?\d*)",
            r"(?:Total|Payable) Amount[:\s]*(?:Rs\.?|₹)?\s*([\d,]+\.?\d*)"
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