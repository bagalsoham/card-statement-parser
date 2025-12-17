from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import date

class ParsedField(BaseModel):
    """Individual field with confidence"""
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    extraction_method: Literal["regex", "table", "layout", "llm"]
    raw_value: Optional[str] = None

class StatementData(BaseModel):
    """Normalized credit card statement data"""
    issuer: ParsedField
    card_last_4: ParsedField
    statement_period: ParsedField
    due_date: ParsedField
    total_amount_due: ParsedField
    
    # Metadata
    overall_confidence: float = Field(ge=0.0, le=1.0)
    parsing_errors: List[str] = []
    fallback_used: bool = False

class ParserResponse(BaseModel):
    """API Response"""
    success: bool
    data: Optional[StatementData] = None
    errors: List[str] = []
    processing_time_ms: float