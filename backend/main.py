from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import time
from typing import Optional
import structlog

from app.pdf_loader import PDFLoader
from app.issuer_detector import IssuerDetector
from app.parsers.hdfc_parser import HDFCParser
from app.parsers.icici_parser import ICICIParser
from app.parsers.sbi_parser import SBIParser
from app.parsers.axis_parser import AxisParser
from app.parsers.amex_parser import AmexParser
from app.schemas import ParserResponse

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

app = FastAPI(
    title="Credit Card Statement Parser",
    description="AI-powered PDF statement parser with LLM fallback supporting 5 major issuers",
    version="2.0.0"
)

# Parser registry - All 5 issuers supported
PARSER_REGISTRY = {
    "HDFC": HDFCParser(),
    "ICICI": ICICIParser(),
    "SBI": SBIParser(),
    "AXIS": AxisParser(),
    "AMEX": AmexParser(),
}

@app.post("/parse-statement", response_model=ParserResponse)
async def parse_statement(file: UploadFile = File(...)):
    """
    Parse credit card statement PDF
    
    - Supports multiple issuers
    - Multi-strategy extraction (regex, tables, LLM)
    - Returns confidence scores
    """
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(400, "Only PDF files are supported")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        logger.info("file_uploaded", filename=file.filename, size=len(content))
        
        # Extract content
        pdf_loader = PDFLoader()
        text = pdf_loader.extract_text(tmp_path)
        tables = pdf_loader.extract_tables(tmp_path)
        
        # Detect issuer
        issuer, issuer_confidence = IssuerDetector.detect(text)
        
        if not issuer:
            return ParserResponse(
                success=False,
                errors=["Could not detect card issuer"],
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Get appropriate parser
        parser = PARSER_REGISTRY.get(issuer)
        
        if not parser:
            return ParserResponse(
                success=False,
                errors=[f"Parser not implemented for {issuer}"],
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Parse statement
        statement_data = parser.parse(text, tables)
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info("parsing_completed", 
                   issuer=issuer,
                   confidence=statement_data.overall_confidence,
                   time_ms=processing_time)
        
        return ParserResponse(
            success=True,
            data=statement_data,
            errors=statement_data.parsing_errors,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error("parsing_failed", error=str(e))
        return ParserResponse(
            success=False,
            errors=[str(e)],
            processing_time_ms=(time.time() - start_time) * 1000
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/supported-issuers")
async def get_supported_issuers():
    """List supported card issuers"""
    return {
        "issuers": list(PARSER_REGISTRY.keys()),
        "count": len(PARSER_REGISTRY)
    }

# ----------------------------------------------------------------------------
# File: test_example.py
# ----------------------------------------------------------------------------
"""
Example usage and testing
"""

if __name__ == "__main__":
    # CLI Usage Example
    import sys
    from app.pdf_loader import PDFLoader
    from app.issuer_detector import IssuerDetector
    from app.parsers.hdfc_parser import HDFCParser
    from app.parsers.icici_parser import ICICIParser
    from app.parsers.sbi_parser import SBIParser
    from app.parsers.axis_parser import AxisParser
    from app.parsers.amex_parser import AmexParser
    
    # Parser registry for CLI
    PARSER_REGISTRY = {
        "HDFC": HDFCParser(),
        "ICICI": ICICIParser(),
        "SBI": SBIParser(),
        "AXIS": AxisParser(),
        "AMEX": AmexParser(),
    }
    
    if len(sys.argv) < 2:
        print("Usage: python test_example.py <pdf_path>")
        print("\nSupported Issuers:")
        print("  • HDFC Bank")
        print("  • ICICI Bank")
        print("  • SBI Card")
        print("  • Axis Bank")
        print("  • American Express")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"CREDIT CARD STATEMENT PARSER v2.0")
    print(f"{'='*60}\n")
    
    # Load PDF
    print("📄 Loading PDF...")
    loader = PDFLoader()
    text = loader.extract_text(pdf_path)
    tables = loader.extract_tables(pdf_path)
    print(f"   ✓ Extracted {len(text)} characters")
    print(f"   ✓ Found {len(tables)} tables\n")
    
    # Detect issuer
    print("🔍 Detecting issuer...")
    issuer, confidence = IssuerDetector.detect(text)
    print(f"   ✓ Detected: {issuer} (confidence: {confidence:.2f})\n")
    
    # Parse
    parser = PARSER_REGISTRY.get(issuer)
    if parser:
        print("⚙️  Parsing statement...")
        result = parser.parse(text, tables)
        
        print(f"\n{'='*60}")
        print(f"PARSING RESULTS")
        print(f"{'='*60}")
        print(f"Overall Confidence: {result.overall_confidence:.2f}")
        print(f"Fallback Used: {'Yes (LLM)' if result.fallback_used else 'No (Regex)'}")
        print(f"\n{'-'*60}")
        
        # Format output with colors/emojis
        fields = [
            ("🏦 Issuer", result.issuer),
            ("💳 Card Last 4", result.card_last_4),
            ("📅 Statement Period", result.statement_period),
            ("⏰ Due Date", result.due_date),
            ("💰 Total Due", result.total_amount_due)
        ]
        
        for label, field in fields:
            method_emoji = {
                "regex": "🔧",
                "table": "📊", 
                "layout": "📐",
                "llm": "🤖"
            }.get(field.extraction_method, "❓")
            
            conf_color = "🟢" if field.confidence >= 0.9 else "🟡" if field.confidence >= 0.7 else "🔴"
            
            value_display = field.value if field.value else "NOT FOUND"
            if label == "💰 Total Due" and field.value:
                value_display = f"₹{field.value}"
            
            print(f"\n{label}")
            print(f"  Value: {value_display}")
            print(f"  Method: {method_emoji} {field.extraction_method.upper()}")
            print(f"  Confidence: {conf_color} {field.confidence:.2f}")
        
        if result.parsing_errors:
            print(f"\n{'-'*60}")
            print("⚠️  WARNINGS:")
            for error in result.parsing_errors:
                print(f"  • {error}")
        
        print(f"\n{'='*60}")
        
        # Summary
        if result.overall_confidence >= 0.9:
            print("✅ HIGH CONFIDENCE - All fields extracted reliably")
        elif result.overall_confidence >= 0.7:
            print("⚠️  MEDIUM CONFIDENCE - Some fields may need verification")
        else:
            print("❌ LOW CONFIDENCE - Manual review recommended")
        
        print(f"{'='*60}\n")
    else:
        print(f"❌ No parser available for {issuer}")
        print(f"   Supported issuers: {', '.join(PARSER_REGISTRY.keys())}")
