from abc import ABC, abstractmethod
from typing import Dict, Optional
import structlog
from app.schemas import ParsedField, StatementData
from app.validators import FieldValidator
from app.config import Config

logger = structlog.get_logger()

class BaseParser(ABC):
    """Enhanced base parser with multi-strategy extraction"""
    
    def __init__(self):
        self.validator = FieldValidator()
        # Only import and instantiate LLM extractor when configured to use it.
        if Config.USE_LLM_FALLBACK:
            from app.llm_extractor import LLMExtractor
            self.llm_extractor = LLMExtractor()
        else:
            self.llm_extractor = None
    
    @abstractmethod
    def extract_with_regex(self, text: str) -> Dict:
        """Issuer-specific regex extraction"""
        pass
    
    def extract_with_tables(self, tables: list) -> Dict:
        """Extract from tables (override if needed)"""
        return {}
    
    def parse(self, text: str, tables: list = None) -> StatementData:
        """
        Multi-strategy parsing pipeline
        1. Try regex
        2. Try tables
        3. Fallback to LLM if needed
        """
        result = {}
        errors = []
        fallback_used = False
        
        # Strategy 1: Regex
        try:
            regex_data = self.extract_with_regex(text)
            result.update(regex_data)
            logger.info("regex_extraction_completed", fields=list(regex_data.keys()))
        except Exception as e:
            errors.append(f"Regex extraction failed: {str(e)}")
            logger.warning("regex_extraction_failed", error=str(e))
        
        # Strategy 2: Tables
        if tables:
            try:
                table_data = self.extract_with_tables(tables)
                result.update(table_data)
            except Exception as e:
                errors.append(f"Table extraction failed: {str(e)}")
        
        # Strategy 3: LLM Fallback
        missing_fields = self._get_missing_fields(result)
        if missing_fields and Config.USE_LLM_FALLBACK and self.llm_extractor:
            try:
                logger.info("using_llm_fallback", missing_fields=missing_fields)
                llm_data = self.llm_extractor.extract_fields(text)
                
                # Fill missing fields with LLM data
                for field in missing_fields:
                    if field in llm_data and llm_data[field]:
                        result[field] = {
                            "value": llm_data[field],
                            "method": "llm"
                        }
                
                fallback_used = True
                logger.info("llm_fallback_completed")
            except Exception as e:
                errors.append(f"LLM fallback failed: {str(e)}")
                logger.error("llm_fallback_failed", error=str(e))
        
        # Convert to ParsedField objects with validation
        return self._build_statement_data(result, errors, fallback_used)
    
    def _get_missing_fields(self, result: Dict) -> list:
        """Identify missing fields"""
        required = ["issuer", "card_last_4", "statement_period", 
                   "due_date", "total_amount_due"]
        
        missing = []
        for field in required:
            if field not in result or not result[field].get("value"):
                missing.append(field)
        
        return missing
    
    def _build_statement_data(self, result: Dict, errors: list, 
                              fallback_used: bool) -> StatementData:
        """Build StatementData with confidence scores"""
        
        parsed_fields = {}
        confidences = []
        
        for field_name in ["issuer", "card_last_4", "statement_period", 
                          "due_date", "total_amount_due"]:
            
            field_data = result.get(field_name, {})
            value = field_data.get("value")
            method = field_data.get("method", "regex")
            
            # Validate and score confidence
            confidence = self._calculate_confidence(field_name, value, method)
            confidences.append(confidence)
            
            parsed_fields[field_name] = ParsedField(
                value=value,
                confidence=confidence,
                extraction_method=method,
                raw_value=value
            )
        
        # Overall confidence is average of all fields
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return StatementData(
            issuer=parsed_fields["issuer"],
            card_last_4=parsed_fields["card_last_4"],
            statement_period=parsed_fields["statement_period"],
            due_date=parsed_fields["due_date"],
            total_amount_due=parsed_fields["total_amount_due"],
            overall_confidence=overall_confidence,
            parsing_errors=errors,
            fallback_used=fallback_used
        )
    
    def _calculate_confidence(self, field_name: str, value: str, 
                             method: str) -> float:
        """Calculate confidence score for a field"""
        if not value:
            return 0.0
        
        # Base confidence by method
        method_confidence = {
            "regex": 0.9,
            "table": 0.85,
            "layout": 0.8,
            "llm": 0.75
        }.get(method, 0.5)
        
        # Validate the value
        validators = {
            "card_last_4": self.validator.validate_card_last_4,
            "due_date": self.validator.validate_date,
            "total_amount_due": self.validator.validate_amount,
            "issuer": self.validator.validate_issuer,
        }
        
        if field_name in validators:
            is_valid, validation_conf = validators[field_name](value)
            if not is_valid:
                return validation_conf * 0.5
            return method_confidence * validation_conf
        
        return method_confidence
