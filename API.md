# API Reference

Complete REST API documentation for the Credit Card Statement Parser.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Request/Response Formats](#requestresponse-formats)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [Examples](#examples)

---

## Base URL

```
Development: http://localhost:8000
Production: https://api.your-domain.com
```

## Authentication

**Current**: No authentication required  
**Future**: API key authentication via header

```http
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Health Check

Check if the API is running and healthy.

**Endpoint**: `GET /health`

**Request**:
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Service status ("healthy" or "unhealthy") |
| `version` | string | API version number |

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is down

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 2. List Supported Issuers

Get a list of all supported credit card issuers.

**Endpoint**: `GET /supported-issuers`

**Request**:
```http
GET /supported-issuers HTTP/1.1
Host: localhost:8000
```

**Response**: `200 OK`
```json
{
  "issuers": [
    "HDFC",
    "ICICI",
    "SBI",
    "AXIS",
    "AMEX"
  ],
  "count": 5
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `issuers` | array[string] | List of supported issuer codes |
| `count` | integer | Total number of supported issuers |

**Status Codes**:
- `200 OK`: Successfully retrieved list

**Example**:
```bash
curl http://localhost:8000/supported-issuers
```

---

### 3. Parse Credit Card Statement

Upload and parse a credit card statement PDF.

**Endpoint**: `POST /parse-statement`

**Request**:
```http
POST /parse-statement HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="statement.pdf"
Content-Type: application/pdf

[Binary PDF data]
------WebKitFormBoundary--
```

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | file | Yes | PDF file to parse (max 10MB) |

**Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "issuer": {
      "value": "HDFC Bank",
      "confidence": 0.95,
      "extraction_method": "regex",
      "raw_value": "HDFC Bank"
    },
    "card_last_4": {
      "value": "4567",
      "confidence": 1.0,
      "extraction_method": "regex",
      "raw_value": "4567"
    },
    "statement_period": {
      "value": "01-Nov-2024 to 30-Nov-2024",
      "confidence": 0.90,
      "extraction_method": "regex",
      "raw_value": "01-Nov-2024 to 30-Nov-2024"
    },
    "due_date": {
      "value": "15-Dec-2024",
      "confidence": 0.92,
      "extraction_method": "regex",
      "raw_value": "15-Dec-2024"
    },
    "total_amount_due": {
      "value": "45678.50",
      "confidence": 1.0,
      "extraction_method": "regex",
      "raw_value": "45678.50"
    },
    "overall_confidence": 0.95,
    "parsing_errors": [],
    "fallback_used": false
  },
  "errors": [],
  "processing_time_ms": 245.67
}
```

**Response Fields**:

#### Top Level
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether parsing was successful |
| `data` | object | Parsed statement data (null if failed) |
| `errors` | array[string] | List of error messages |
| `processing_time_ms` | float | Processing time in milliseconds |

#### Data Object
| Field | Type | Description |
|-------|------|-------------|
| `issuer` | ParsedField | Card issuer/bank name |
| `card_last_4` | ParsedField | Last 4 digits of card number |
| `statement_period` | ParsedField | Billing cycle dates |
| `due_date` | ParsedField | Payment due date |
| `total_amount_due` | ParsedField | Total outstanding amount |
| `overall_confidence` | float | Average confidence (0.0-1.0) |
| `parsing_errors` | array[string] | Non-fatal parsing warnings |
| `fallback_used` | boolean | Whether LLM fallback was used |

#### ParsedField Object
| Field | Type | Description |
|-------|------|-------------|
| `value` | string | Extracted value (null if not found) |
| `confidence` | float | Confidence score (0.0-1.0) |
| `extraction_method` | string | Method used: "regex", "table", "layout", "llm" |
| `raw_value` | string | Original unprocessed value |

**Status Codes**:
- `200 OK`: Parsing completed (check `success` field)
- `400 Bad Request`: Invalid file or format
- `413 Payload Too Large`: File exceeds 10MB
- `422 Unprocessable Entity`: Missing required fields
- `500 Internal Server Error`: Server error

**Error Response**: `400 Bad Request`
```json
{
  "success": false,
  "data": null,
  "errors": [
    "Only PDF files are supported",
    "File size exceeds 10MB limit"
  ],
  "processing_time_ms": 5.23
}
```

**Examples**:

**cURL**:
```bash
curl -X POST "http://localhost:8000/parse-statement" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@hdfc_statement.pdf"
```

**Python**:
```python
import requests

url = "http://localhost:8000/parse-statement"
files = {"file": open("statement.pdf", "rb")}

response = requests.post(url, files=files)
data = response.json()

if data["success"]:
    print(f"Card: ****{data['data']['card_last_4']['value']}")
    print(f"Amount: ₹{data['data']['total_amount_due']['value']}")
else:
    print(f"Errors: {data['errors']}")
```

**JavaScript**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/parse-statement', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Card:', data.data.card_last_4.value);
      console.log('Amount:', data.data.total_amount_due.value);
    } else {
      console.error('Errors:', data.errors);
    }
  });
```

---

## Request/Response Formats

### Content Types

**Request**:
- `multipart/form-data` for file uploads
- `application/json` for JSON data (future endpoints)

**Response**:
- Always `application/json`

### Date Formats

Dates are returned in their original format from the statement:

- `DD-MMM-YYYY` (e.g., "15-Dec-2024")
- `DD/MM/YYYY` (e.g., "15/12/2024")
- `MMM DD, YYYY` (e.g., "Dec 15, 2024")

### Amount Formats

Amounts are returned as numeric strings without currency symbols:

- `"45678.50"` (not "₹45,678.50")
- Always includes decimal point
- No thousands separators

### Confidence Scores

All confidence scores are floats between 0.0 and 1.0:

- `1.0`: Perfect confidence
- `0.9-0.99`: High confidence
- `0.7-0.89`: Medium confidence
- `< 0.7`: Low confidence (requires review)

### Extraction Methods

- `"regex"`: Rule-based pattern matching
- `"table"`: Extracted from table structures
- `"layout"`: Position-based extraction
- `"llm"`: AI-powered extraction (Google Gemini)

---

## Error Handling

### Error Response Format

All errors return this structure:

```json
{
  "success": false,
  "data": null,
  "errors": [
    "Error message 1",
    "Error message 2"
  ],
  "processing_time_ms": 12.34
}
```

### Common Errors

#### 400 Bad Request

**Causes**:
- File is not a PDF
- File exceeds size limit
- Corrupted PDF

**Example**:
```json
{
  "success": false,
  "data": null,
  "errors": ["Only PDF files are supported"],
  "processing_time_ms": 3.21
}
```

#### 422 Unprocessable Entity

**Causes**:
- Missing required fields
- Invalid field types

**Example**:
```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error

**Causes**:
- Server error
- Uncaught exception

**Example**:
```json
{
  "success": false,
  "data": null,
  "errors": ["Internal server error occurred"],
  "processing_time_ms": 100.5
}
```

### Partial Success

Even if some fields fail to extract, the API returns `success: true` with whatever data was extracted:

```json
{
  "success": true,
  "data": {
    "issuer": {
      "value": "HDFC Bank",
      "confidence": 0.95,
      "extraction_method": "regex",
      "raw_value": "HDFC Bank"
    },
    "card_last_4": {
      "value": null,
      "confidence": 0.0,
      "extraction_method": "regex",
      "raw_value": null
    },
    // ... other fields
    "overall_confidence": 0.47,
    "parsing_errors": ["Failed to extract card number"],
    "fallback_used": true
  },
  "errors": [],
  "processing_time_ms": 1234.56
}
```

Check `overall_confidence` and `parsing_errors` to determine data quality.

---

## Rate Limits

**Current**: No rate limits

**Future**: 
- **Free tier**: 100 requests/hour
- **Premium tier**: 1000 requests/hour

Rate limit headers (future):
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## CORS Configuration

**Allowed Origins**:
- `http://localhost:3000` (React dev)
- `http://localhost:5173` (Vite dev)
- `http://127.0.0.1:3000`

**Allowed Methods**:
- `GET`
- `POST`
- `OPTIONS`

**Allowed Headers**:
- `Content-Type`
- `Authorization` (future)

---

## WebSocket Support

**Status**: Not implemented

**Future**: Real-time updates for long-running processing

```javascript
// Future API
const ws = new WebSocket('ws://localhost:8000/ws/parse');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Progress:', update.stage, update.progress);
};
```

---

## Batch Processing

**Status**: Not implemented

**Future**: Upload multiple PDFs at once

```http
POST /parse-statement/batch HTTP/1.1
Content-Type: multipart/form-data

files[]: file1.pdf
files[]: file2.pdf
files[]: file3.pdf
```

---

## Webhooks

**Status**: Not implemented

**Future**: Receive callbacks when processing completes

```http
POST /parse-statement?webhook_url=https://your-site.com/callback HTTP/1.1
```

---

## SDK Examples

### Python SDK (Future)

```python
from cc_parser import CCParser

parser = CCParser(api_key="your-key")
result = parser.parse("statement.pdf")

if result.success:
    print(f"Issuer: {result.data.issuer.value}")
    print(f"Amount: {result.data.total_amount_due.value}")
```

### Node.js SDK (Future)

```javascript
const { CCParser } = require('@ccparser/node');

const parser = new CCParser({ apiKey: 'your-key' });

parser.parse('statement.pdf').then(result => {
  if (result.success) {
    console.log('Issuer:', result.data.issuer.value);
    console.log('Amount:', result.data.totalAmountDue.value);
  }
});
```

---

## Interactive Documentation

**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

Interactive documentation allows you to:
- View all endpoints
- Try API calls directly
- See request/response schemas
- Download OpenAPI specification

---

## Performance Tips

### 1. Optimize File Size

Compress PDFs before uploading:
```bash
# Using Ghostscript
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=compressed.pdf input.pdf
```

### 2. Reuse Connections

Use connection pooling:
```python
import requests

session = requests.Session()
for pdf in pdfs:
    response = session.post(url, files={"file": open(pdf, "rb")})
```

### 3. Parallel Processing

Process multiple PDFs concurrently:
```python
import asyncio
import aiohttp

async def parse_pdf(session, pdf_path):
    async with session.post(url, data={"file": open(pdf_path, "rb")}) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [parse_pdf(session, pdf) for pdf in pdf_files]
        results = await asyncio.gather(*tasks)
```

---

## Changelog

### API Version 2.0.0 (2024-12-17)

**Added**:
- `/parse-statement` endpoint
- Per-field confidence scores
- Multiple extraction methods
- LLM fallback support

**Changed**:
- Response format now includes confidence scores
- Error handling improved

### API Version 1.0.0 (2024-10-01)

**Added**:
- `/health` endpoint
- `/supported-issuers` endpoint
- Basic parsing functionality

---

## Support

- **Issues**: [GitHub Issues](https://github.com/your-username/credit-card-parser/issues)
- **API Status**: [Status Page](https://status.your-domain.com)
- **Email**: api-support@your-domain.com

---

**Last Updated**: 2024-12-17  
**API Version**: 2.0.0