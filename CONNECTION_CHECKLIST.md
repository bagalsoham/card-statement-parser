# Backend & Frontend Connection Checklist

## ✅ Configuration Status

### Backend (FastAPI)
- **Port**: 8000
- **URL**: http://localhost:8000
- **CORS**: ✅ ENABLED (supports localhost:3000 and localhost:5173)
- **Required Dependency**: fastapi-cors==0.0.6 (added to requirements.txt)

### Frontend (React)
- **Port**: 3000 (default React dev server)
- **API Base URL**: http://localhost:8000
- **CORS Ready**: ✅ YES

---

## 📋 Connection Verification

### Backend Endpoints Available
1. ✅ `GET /health` - Health check endpoint
2. ✅ `GET /supported-issuers` - List supported card issuers
3. ✅ `POST /parse-statement` - Parse PDF statement

### Frontend Integration Points
1. ✅ Health check on app mount
2. ✅ Fetch supported issuers on app mount
3. ✅ File upload with drag-drop support
4. ✅ Backend status indicator (online/offline)
5. ✅ Error handling for offline backend

---

## 🚀 Setup Instructions

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```
Expected output: `Uvicorn running on http://127.0.0.1:8000`

### 3. Start Frontend Server
```bash
cd frontend
npm start
```
Expected output: `webpack compiled with ... warning` → Opens http://localhost:3000

### 4. Verify Connection
- Frontend should show "Backend Online" indicator (green dot)
- Supported issuers should display: HDFC, ICICI, SBI, AXIS, AMEX
- Upload button should be enabled

---

## 🔍 Troubleshooting

### Issue: "Backend Offline" Message
**Cause**: Backend not running or CORS issue
**Solution**:
1. Verify backend is running on port 8000
2. Check CORS configuration in backend/main.py
3. Ensure fastapi-cors is installed: `pip install fastapi-cors`

### Issue: Network Error on File Upload
**Cause**: Backend crashed or connectivity issue
**Solution**:
1. Check backend logs for errors
2. Verify frontend API URL is correct: http://localhost:8000
3. Test with curl: `curl http://localhost:8000/health`

### Issue: No Supported Issuers Display
**Cause**: Frontend fetch failed
**Solution**:
1. Check browser console for error messages
2. Verify `/supported-issuers` endpoint is accessible
3. Check network tab in developer tools

---

## 📊 Request/Response Format

### Health Check
```
GET /health
Response: {"status": "healthy", "version": "2.0.0"}
```

### Supported Issuers
```
GET /supported-issuers
Response: {"issuers": ["HDFC", "ICICI", "SBI", "AXIS", "AMEX"], "count": 5}
```

### Parse Statement
```
POST /parse-statement
Content-Type: multipart/form-data
Body: { "file": <PDF_FILE> }

Response: {
  "success": true,
  "data": {
    "issuer": "HDFC",
    "card_last_4": "1234",
    "statement_period": "01-Dec-2024 to 31-Dec-2024",
    "due_date": "15-Jan-2025",
    "total_amount_due": "50000.00",
    "overall_confidence": 0.95,
    "fallback_used": false
  },
  "errors": [],
  "processing_time_ms": 2345
}
```

---

## ✨ Features Verified

- [x] CORS middleware configured
- [x] Health check endpoint working
- [x] Supported issuers endpoint implemented
- [x] Frontend API base URL correct
- [x] Frontend health check logic
- [x] Frontend issuer fetching logic
- [x] File upload error handling
- [x] Backend status indicator
- [x] Processing time display
- [x] Confidence scoring display

---

**Last Updated**: December 17, 2025
**Status**: Ready for testing ✅
