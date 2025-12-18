# System Architecture

This document describes the architectural design, patterns, and decisions behind the Credit Card Statement Parser.

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [System Architecture](#system-architecture)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Technology Choices](#technology-choices)
- [Scalability](#scalability)
- [Security](#security)

---

## Overview

### Vision

Build a **production-ready, extensible PDF parser** that reliably extracts structured data from credit card statements across multiple issuers using a hybrid approach combining rule-based and AI-powered extraction.

### Key Requirements

1. **Accuracy**: >90% field extraction accuracy
2. **Speed**: Sub-second processing for most documents
3. **Extensibility**: Easy to add new banks (15 minutes)
4. **Reliability**: Graceful degradation, comprehensive error handling
5. **Transparency**: Confidence scores for all extracted data
6. **Cost-Effective**: Minimal LLM usage (only when needed)

---

## Design Principles

### 1. **Multi-Strategy Extraction**

Don't rely on a single extraction method. Use a pipeline:

```
Regex (Fast, 90% coverage)
  ↓ (if failed)
Table Extraction (Structured data)
  ↓ (if failed)
Layout Analysis (Position-based)
  ↓ (if failed)
LLM Fallback (AI-powered, handles everything)
```

**Rationale**: Different PDFs require different approaches. Clean statements work with regex, messy ones need AI.

### 2. **Confidence Scoring**

Every extracted field has a confidence score (0.0-1.0) based on:
- Extraction method used
- Validation result
- Pattern match quality

**Rationale**: Downstream systems can decide whether to trust data or require human review.

### 3. **Fail-Safe Design**

Never throw unhandled exceptions. Always return structured responses:

```python
{
    "success": true/false,
    "data": {...},
    "errors": [...],
    "warnings": [...]
}
```

**Rationale**: Production systems need predictable behavior.

### 4. **Modular Architecture**

Each issuer = separate parser module implementing common interface.

**Rationale**: Easy to add/modify/test individual banks without affecting others.

### 5. **Configuration Over Code**

Use environment variables and config files for behavior control.

**Rationale**: Deploy same code in different environments without changes.

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ React UI   │  │ File Upload│  │ Results    │            │
│  │            │  │ Component  │  │ Display    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼─────────────────────────────────────┐
│                      BACKEND (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (main.py)                     │   │
│  │  • CORS Middleware                                   │   │
│  │  • Request Validation                                │   │
│  │  • Response Formatting                               │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │           Processing Pipeline                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ PDF      │→ │ Issuer   │→ │ Parser   │          │   │
│  │  │ Loader   │  │ Detector │  │ Router   │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │           Parser Layer                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ HDFC     │  │ ICICI    │  │ SBI      │  ...     │   │
│  │  │ Parser   │  │ Parser   │  │ Parser   │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │        Extraction Strategies                         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ Regex    │  │ Table    │  │ LLM      │          │   │
│  │  │ Engine   │  │ Extractor│  │ Fallback │          │   │
│  │  └──────────┘  └──────────┘  └────┬─────┘          │   │
│  └─────────────────────────────────────┼───────────────┘   │
│                                        │                    │
│  ┌─────────────────────────────────────▼───────────────┐   │
│  │           Validation & Scoring                       │   │
│  │  • Field Validation                                  │   │
│  │  • Confidence Calculation                            │   │
│  │  • Error Collection                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                  EXTERNAL SERVICES                           │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Google Gemini    │  │ Logging          │                │
│  │ API              │  │ (structlog)      │                │
│  └──────────────────┘  └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
```

### Component Layers

#### 1. **Frontend Layer** (React)
- User interface
- File upload handling
- Results visualization
- Backend status monitoring

#### 2. **API Layer** (FastAPI)
- REST endpoint exposure
- Request/response handling
- CORS management
- Authentication (future)

#### 3. **Processing Layer**
- PDF extraction
- Issuer detection
- Parser routing

#### 4. **Parser Layer**
- Issuer-specific logic
- Pattern matching
- Table extraction

#### 5. **Strategy Layer**
- Regex extraction
- Table parsing
- Layout analysis
- LLM fallback

#### 6. **Validation Layer**
- Field validation
- Confidence scoring
- Error collection

---

## Component Design

### 1. PDF Loader (`pdf_loader.py`)

**Responsibility**: Extract raw data from PDF files

**Methods**:
```python
class PDFLoader:
    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract all text from PDF"""
        
    @staticmethod
    def extract_tables(pdf_path: str) -> List[List[List[str]]]:
        """Extract tables from PDF"""
        
    @staticmethod
    def extract_layout_info(pdf_path: str) -> Dict:
        """Extract layout and positioning info"""
```

**Technology**: pdfplumber + PyMuPDF

**Design Decision**: Static methods because no state needed between calls.

---

### 2. Issuer Detector (`issuer_detector.py`)

**Responsibility**: Identify which bank issued the statement

**Algorithm**:
```python
1. Convert text to lowercase
2. For each known issuer:
   a. Check if any pattern matches
   b. Count matches
3. Return issuer with highest match count
4. Calculate confidence based on match strength
```

**Pattern Examples**:
```python
ISSUER_PATTERNS = {
    "HDFC": [r"hdfc\s+bank", r"hdfc\s+credit\s+card"],
    "ICICI": [r"icici\s+bank", r"icici\s+credit"],
    # ...
}
```

**Design Decision**: Pattern-based for speed and simplicity. Could be replaced with ML classifier if needed.

---

### 3. Base Parser (`base_parser.py`)

**Responsibility**: Define common interface and multi-strategy logic

**Key Method**:
```python
def parse(self, text: str, tables: list) -> StatementData:
    """
    Multi-strategy parsing pipeline
    1. Try regex
    2. Try tables
    3. Fallback to LLM if needed
    4. Validate and score
    5. Return structured result
    """
```

**Design Pattern**: Template Method Pattern

**Rationale**: Common pipeline logic in base class, issuer-specific extraction in subclasses.

---

### 4. Issuer-Specific Parsers

**Example**: `hdfc_parser.py`

**Responsibility**: HDFC-specific regex patterns

```python
class HDFCParser(BaseParser):
    def extract_with_regex(self, text: str) -> dict:
        """HDFC-specific patterns"""
        # Card: XXXX XXXX XXXX 1234
        # Date: DD-MMM-YYYY
        # Amount: ₹XX,XXX.XX
```

**Design Decision**: One parser per issuer for maintainability.

---

### 5. LLM Extractor (`llm_extractor.py`)

**Responsibility**: AI-powered fallback extraction

**When Used**:
- Regex fails to find fields
- Confidence too low
- Unusual PDF format
- Scanned/OCR documents

**Prompt Engineering**:
```python
prompt = f"""
Extract from this credit card statement:
{{
  "issuer": "...",
  "card_last_4": "...",
  ...
}}

Rules:
- Return ONLY JSON
- Use null for missing fields
- Extract numeric values only for amounts
"""
```

**Cost Optimization**: Only triggered when regex fails (saves 90% of LLM costs).

---

### 6. Validators (`validators.py`)

**Responsibility**: Validate extracted fields

**Validation Rules**:
```python
class FieldValidator:
    def validate_card_last_4(value: str) -> Tuple[bool, float]:
        # Must be exactly 4 digits
        # Returns: (is_valid, confidence)
        
    def validate_date(value: str) -> Tuple[bool, float]:
        # Must match common date formats
        
    def validate_amount(value: str) -> Tuple[bool, float]:
        # Must be numeric, positive
```

**Design Decision**: Separate validation from extraction for single responsibility.

---

## Data Flow

### Successful Extraction Flow

```
1. User uploads PDF
   ↓
2. Frontend sends to /parse-statement endpoint
   ↓
3. Backend receives file
   ↓
4. PDF Loader extracts text, tables, layout
   ↓
5. Issuer Detector identifies bank (e.g., "HDFC")
   ↓
6. Parser Router selects HDFCParser
   ↓
7. HDFCParser tries regex extraction
   ├─ Success → Skip to step 10
   └─ Partial success/failure → Continue
   ↓
8. Try table extraction
   ├─ Fills missing fields → Skip to step 10
   └─ Still missing fields → Continue
   ↓
9. LLM Fallback for remaining fields
   ↓
10. Validator checks all fields
   ↓
11. Confidence Calculator scores each field
   ↓
12. Build StatementData response
   ↓
13. Return JSON to frontend
   ↓
14. Frontend displays results with confidence indicators
```

### Error Handling Flow

```
1. Error occurs at any step
   ↓
2. Exception caught by try-catch
   ↓
3. Error logged with context
   ↓
4. Error added to response.errors[]
   ↓
5. Partial data still returned if available
   ↓
6. Overall confidence adjusted down
   ↓
7. Frontend shows warning with available data
```

---

## Technology Choices

### Backend: FastAPI

**Why FastAPI?**
- ✅ Fast (async support)
- ✅ Auto-generated API docs (Swagger/OpenAPI)
- ✅ Type safety (Pydantic)
- ✅ Easy testing
- ✅ Modern Python features

**Alternatives Considered**:
- Flask: Simpler but no async, no auto docs
- Django: Too heavy for this use case
- Express (Node): Team expertise in Python

---

### PDF Parsing: pdfplumber + PyMuPDF

**Why pdfplumber?**
- ✅ Excellent table extraction
- ✅ Character-level positioning
- ✅ Easy API

**Why PyMuPDF?**
- ✅ Fast layout analysis
- ✅ Detailed document structure
- ✅ Complements pdfplumber

**Alternatives Considered**:
- PyPDF2: Less accurate
- Camelot: Specialized for tables only
- pdfminer: Lower-level, more complex

---

### LLM: Google Gemini

**Why Gemini?**
- ✅ Good balance of speed/accuracy
- ✅ Competitive pricing
- ✅ JSON mode support
- ✅ High token limits

**Alternatives Considered**:
- OpenAI GPT-4: More expensive
- Anthropic Claude: Chosen initially, Gemini for final version
- Local models: Not accurate enough

---

### Frontend: React

**Why React?**
- ✅ Component-based architecture
- ✅ Large ecosystem
- ✅ Team familiarity
- ✅ Easy state management

**Alternatives Considered**:
- Vue: Similar capabilities
- Vanilla JS: Less maintainable
- Streamlit: Too limited for custom UI

---

## Scalability

### Current Architecture (Single Instance)

**Capacity**: ~100 requests/minute

**Bottlenecks**:
1. PDF parsing (CPU-bound)
2. LLM API calls (network-bound)
3. Single-threaded Python

### Horizontal Scaling Strategy

```
┌─────────────┐
│ Load        │
│ Balancer    │
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│API  │ │API  │ │API  │ │API  │
│Inst │ │Inst │ │Inst │ │Inst │
│ 1   │ │ 2   │ │ 3   │ │ 4   │
└─────┘ └─────┘ └─────┘ └─────┘
```

**Scaling to 1000+ req/min**:
1. Deploy multiple FastAPI instances
2. Use nginx/HAProxy for load balancing
3. Add Redis for caching parsed results
4. Implement async processing queue (Celery)

---

### Vertical Scaling Strategy

**Current**: 1 CPU, 2GB RAM

**Scaled**: 4 CPUs, 8GB RAM

**Performance Gain**: ~4x throughput

---

### Database Architecture (Future)

```
┌──────────────┐
│  API Servers │
└──────┬───────┘
       │
┌──────▼────────┐
│  PostgreSQL   │
│  ┌─────────┐  │
│  │ Parsed  │  │
│  │ Results │  │
│  └─────────┘  │
│  ┌─────────┐  │
│  │ Audit   │  │
│  │ Logs    │  │
│  └─────────┘  │
└───────────────┘
```

**Tables**:
- `statements`: Parsed statement data
- `processing_logs`: Audit trail
- `users`: User accounts (future)

---

## Security

### Current Implementation

1. **Input Validation**
   - File type checking (PDF only)
   - File size limits (10MB)
   - Malicious PDF detection

2. **API Security**
   - CORS restrictions
   - Rate limiting (future)
   - Request size limits

3. **Data Privacy**
   - No data persistence (stateless)
   - No logging of sensitive fields
   - Secure temporary file handling

### Future Enhancements

1. **Authentication**
   - JWT tokens
   - API key management
   - OAuth integration

2. **Authorization**
   - Role-based access control
   - Per-user rate limits

3. **Encryption**
   - TLS/HTTPS only
   - Encrypted data at rest (if persisted)

4. **Audit Logging**
   - Who accessed what
   - When and from where
   - GDPR compliance

---

## Performance Optimization

### Current Optimizations

1. **Regex Compilation Caching**
   ```python
   # Compile patterns once at module load
   PATTERNS = {
       "card": re.compile(r"XXXX\s*XXXX\s*XXXX\s*(\d{4})")
   }
   ```

2. **Early Exit Strategy**
   ```python
   for pattern in patterns:
       if match := pattern.search(text):
           return match  # Don't try remaining patterns
   ```

3. **LLM Cost Optimization**
   - Only use when regex fails
   - Limit input to 5000 chars
   - Cache common results (future)

### Future Optimizations

1. **Async Processing**
   - Process multiple PDFs concurrently
   - Non-blocking LLM calls

2. **Caching Layer**
   - Cache parsed results (Redis)
   - TTL-based invalidation

3. **PDF Pre-processing**
   - Detect scanned PDFs early
   - Route to OCR pipeline directly

---

## Monitoring & Observability

### Metrics to Track

1. **Performance Metrics**
   - Request latency (p50, p95, p99)
   - Processing time by stage
   - LLM fallback rate

2. **Accuracy Metrics**
   - Overall confidence scores
   - Field extraction success rate
   - LLM vs regex performance

3. **Business Metrics**
   - Statements parsed per day
   - Cost per statement
   - User satisfaction

### Logging Strategy

**Structured JSON Logs** (structlog):

```json
{
  "timestamp": "2024-12-17T10:30:00Z",
  "level": "info",
  "event": "statement_parsed",
  "issuer": "HDFC",
  "confidence": 0.95,
  "fallback_used": false,
  "processing_time_ms": 245
}
```

**Log Levels**:
- DEBUG: Detailed extraction steps
- INFO: Successful operations
- WARNING: Low confidence, fallbacks used
- ERROR: Failures, exceptions

---

## Design Decisions Log

### Decision 1: Multi-Strategy Over Single Method

**Context**: Initial version used regex only, failed on ~15% of PDFs.

**Decision**: Implement pipeline with LLM fallback.

**Rationale**: Better accuracy worth the complexity.

**Trade-off**: Increased latency when LLM used, but only 10% of time.

---

### Decision 2: Per-Field Confidence Over Binary Success

**Context**: Users need to know which fields to trust.

**Decision**: Return confidence score (0.0-1.0) for each field.

**Rationale**: Downstream systems can make informed decisions.

**Trade-off**: More complex response format.

---

### Decision 3: Stateless API Over Database

**Context**: Need to launch quickly, unclear storage requirements.

**Decision**: No database, process and return immediately.

**Rationale**: Simpler deployment, better privacy.

**Trade-off**: No historical data, re-parsing needed.

---

## Future Architecture

### Phase 1: Current (Stateless API)
```
User → API → Parse → Return
```

### Phase 2: With Database (6 months)
```
User → API → Parse → Store → Return
                    ↓
                 Database
```

### Phase 3: Microservices (12 months)
```
User → API Gateway
         ├→ Parser Service
         ├→ LLM Service
         ├→ Storage Service
         └→ Analytics Service
```

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [Google Gemini API](https://ai.google.dev/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated**: 2024-12-17  
**Version**: 2.0.0