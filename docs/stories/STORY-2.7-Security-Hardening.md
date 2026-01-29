# Story 2.7: Security Hardening

**Story ID**: STORY-2.7
**Epic**: EPIC-02 (API Layer - Security)
**Status**: Draft
**Priority**: P0 (Critical - Security)
**Sprint**: Sprint 2 (Security Hardening)
**Assigned to**: @dev (Dex)
**Estimate**: 0.5 dia

---

## 📖 User Story

**As a** security engineer
**I want** API hardened against common attacks
**So that** the system is protected from vulnerabilities

---

## ✅ Acceptance Criteria

- [ ] CORS configured with specific origins (no wildcard)
- [ ] CSV content validated before processing
- [ ] UUID format validated for job_id
- [ ] Path traversal prevented
- [ ] Input sanitization implemented
- [ ] Security headers added
- [ ] Error messages don't leak sensitive info
- [ ] All validations have tests

---

## 🎯 Context & Requirements

### Security Issues Addressed
From QA Review (EPIC-02-QA-GATE.md):
- 🔴 **CORS Wildcard** (Risk Score: 8/10)
- 🟡 **Path Traversal** (Risk Score: 4/10)
- 🟡 **CSV Injection** (Risk Score: 4/10)

### Technical Approach
- Fix CORS configuration
- Add input validation
- Implement security headers
- Sanitize error messages

---

## 📋 Implementation Tasks

### Task 1: Fix CORS Configuration
**Subtasks:**
- [ ] Remove `allow_origins=["*"]`
- [ ] Add environment variable `ALLOWED_ORIGINS`
- [ ] Default to localhost only
- [ ] Document production configuration
- [ ] Validate origins on startup

### Task 2: CSV Content Validation
**Subtasks:**
- [ ] Validate CSV structure on upload
- [ ] Check for malformed CSV
- [ ] Limit column count (prevent memory bomb)
- [ ] Limit row count estimate
- [ ] Reject suspicious content

### Task 3: UUID Validation
**Subtasks:**
- [ ] Validate job_id format in all endpoints
- [ ] Return 400 for invalid UUIDs
- [ ] Prevent path traversal via job_id
- [ ] Add validation helper function

### Task 4: Security Headers
**Subtasks:**
- [ ] Add CSP header
- [ ] Add X-Content-Type-Options
- [ ] Add X-Frame-Options
- [ ] Add Strict-Transport-Security (HTTPS only)
- [ ] Add X-XSS-Protection

### Task 5: Error Message Sanitization
**Subtasks:**
- [ ] Don't expose file paths in errors
- [ ] Don't expose stack traces
- [ ] Generic errors for production
- [ ] Detailed errors only in dev mode
- [ ] Log sensitive info, don't return it

### Task 6: Testing
**Subtasks:**
- [ ] Test CORS enforcement
- [ ] Test CSV validation
- [ ] Test UUID validation
- [ ] Test security headers present
- [ ] Test error sanitization

---

## 🔒 Security Implementation

### 1. CORS Configuration

**File**: `backend/src/moodlelogsmart/main.py`

```python
import os

# Load allowed origins from environment
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Validate configuration
if "*" in ALLOWED_ORIGINS:
    logger.warning("⚠️ CORS wildcard detected! Not recommended for production")

# Configure CORS securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["Content-Type", "X-API-Key"],  # Only needed headers
    max_age=3600,  # Cache preflight for 1 hour
)

logger.info(f"CORS configured for origins: {ALLOWED_ORIGINS}")
```

**Environment**:
```bash
# Development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Production
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

### 2. CSV Content Validation

**File**: `backend/src/moodlelogsmart/api/validators.py`

```python
"""Input validation utilities."""

import csv
import io
from typing import Tuple
from fastapi import HTTPException

MAX_COLUMNS = 100  # Prevent memory bomb
MAX_ROWS_PREVIEW = 10000  # Check first 10k rows


def validate_csv_content(content: bytes) -> Tuple[bool, str]:
    """Validate CSV file structure and content.

    Args:
        content: CSV file bytes

    Returns:
        (is_valid, error_message)

    Raises:
        HTTPException: If CSV is malformed or suspicious
    """
    try:
        # Decode and check if valid CSV
        text = content.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        raise HTTPException(400, "File encoding must be UTF-8")

    # Use CSV sniffer to detect format
    try:
        sample = text[:4096]  # First 4KB
        csv.Sniffer().sniff(sample)
    except csv.Error as e:
        raise HTTPException(400, f"Invalid CSV format: {str(e)}")

    # Parse and validate structure
    try:
        reader = csv.reader(io.StringIO(text))
        header = next(reader, None)

        if not header:
            raise HTTPException(400, "CSV file is empty")

        # Check column count
        if len(header) > MAX_COLUMNS:
            raise HTTPException(
                400,
                f"Too many columns ({len(header)}), max {MAX_COLUMNS}"
            )

        # Check for suspicious patterns (CSV injection)
        for field in header:
            if field.startswith(('=', '+', '-', '@')):
                raise HTTPException(
                    400,
                    "CSV contains potentially unsafe formula characters"
                )

        # Check row count (sample)
        row_count = 1  # Header
        for i, row in enumerate(reader):
            if i >= MAX_ROWS_PREVIEW:
                break
            row_count += 1

            # Validate row has consistent columns
            if len(row) != len(header):
                logger.warning(
                    f"Row {row_count} has {len(row)} columns, "
                    f"expected {len(header)}"
                )

        logger.info(f"CSV validated: {len(header)} columns, ~{row_count} rows")
        return True, ""

    except Exception as e:
        logger.error(f"CSV validation error: {e}")
        raise HTTPException(400, "CSV validation failed")
```

**Apply in upload endpoint**:
```python
@app.post("/api/upload")
async def upload_csv(...):
    # ... existing code ...

    contents = await file.read()

    # NEW: Validate CSV content
    validate_csv_content(contents)

    # ... rest of code ...
```

---

### 3. UUID Validation

**File**: `backend/src/moodlelogsmart/api/validators.py`

```python
import uuid
from fastapi import HTTPException


def validate_job_id(job_id: str) -> str:
    """Validate job ID is a valid UUID.

    Args:
        job_id: Job identifier to validate

    Returns:
        Validated job_id (normalized)

    Raises:
        HTTPException: 400 if invalid UUID
    """
    try:
        # Parse and validate UUID
        parsed = uuid.UUID(job_id)
        # Return normalized form (lowercase, with hyphens)
        return str(parsed)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid job ID format. Must be a valid UUID"
        )
```

**Apply in endpoints**:
```python
@app.get("/api/status/{job_id}")
async def get_status(job_id: str) -> StatusResponse:
    """Get job processing status."""
    # Validate UUID format
    job_id = validate_job_id(job_id)

    job = job_manager.get_job(job_id)
    # ... rest of code ...
```

---

### 4. Security Headers Middleware

**File**: `backend/src/moodlelogsmart/main.py`

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
        )

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HTTPS only (if in production)
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


# Apply middleware
app.add_middleware(SecurityHeadersMiddleware)
```

---

### 5. Error Message Sanitization

**File**: `backend/src/moodlelogsmart/main.py`

```python
import os
from fastapi import Request, status
from fastapi.responses import JSONResponse


# Check if in development mode
IS_DEVELOPMENT = os.getenv("ENVIRONMENT", "development") == "development"


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""

    # Log full error with stack trace
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"path": request.url.path}
    )

    # Return sanitized error to client
    if IS_DEVELOPMENT:
        # In dev, show detailed errors
        detail = f"{type(exc).__name__}: {str(exc)}"
    else:
        # In production, generic error
        detail = "Internal server error. Please contact support."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "request_id": str(uuid.uuid4())  # For support lookup
        }
    )
```

---

## 🧪 Testing Strategy

### Test: CORS Enforcement
```python
def test_cors_rejects_unauthorized_origin(client):
    """Test CORS rejects requests from unauthorized origins."""
    response = client.get(
        "/health",
        headers={"Origin": "https://evil.com"}
    )

    # Should succeed but not include CORS headers
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_allows_authorized_origin(client):
    """Test CORS allows authorized origins."""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"}
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
```

### Test: CSV Validation
```python
def test_csv_validation_rejects_formula(client):
    """Test CSV validation rejects formulas."""
    malicious_csv = b"=1+1,normal\ndata,data"

    response = client.post(
        "/api/upload",
        files={"file": ("evil.csv", malicious_csv, "text/csv")},
        headers={"X-API-Key": "test-key"}
    )

    assert response.status_code == 400
    assert "unsafe formula" in response.json()["detail"].lower()
```

### Test: UUID Validation
```python
def test_invalid_job_id_format(client):
    """Test invalid job ID returns 400."""
    response = client.get(
        "/api/status/not-a-uuid",
        headers={"X-API-Key": "test-key"}
    )

    assert response.status_code == 400
    assert "Invalid job ID" in response.json()["detail"]
```

### Test: Security Headers
```python
def test_security_headers_present(client):
    """Test security headers are added."""
    response = client.get("/health")

    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"

    assert "Content-Security-Policy" in response.headers
```

---

## 📝 Environment Configuration

### .env.example
```bash
# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Environment
ENVIRONMENT=development  # or "production"

# Validation Limits
MAX_CSV_COLUMNS=100
MAX_CSV_ROWS=1000000
```

---

## 📝 Dev Agent Record

### Checklist
- [ ] Task 1: CORS fixed
- [ ] Task 2: CSV validation implemented
- [ ] Task 3: UUID validation added
- [ ] Task 4: Security headers middleware
- [ ] Task 5: Error sanitization
- [ ] Task 6: Tests passing

### Debug Log
[Will be updated during development]

### Completion Notes
[Will be updated upon completion]

### File List
**Files to Create:**
- [ ] `backend/src/moodlelogsmart/api/validators.py`

**Files to Modify:**
- [ ] `backend/src/moodlelogsmart/main.py` (CORS, headers, errors)
- [ ] `backend/.env.example` (add ALLOWED_ORIGINS)
- [ ] `backend/tests/test_api.py` (add security tests)
- [ ] `backend/README.md` (document security config)

**Files to Delete:**
- [ ] None

### Change Log
[Will add commits during development]

---

## 📚 References

**QA Review**: docs/qa/gates/EPIC-02-QA-GATE.md
**CORS Wildcard Risk**: Score 8/10
**CSV Injection Risk**: Score 4/10
**OWASP Top 10**: https://owasp.org/www-project-top-ten/

---

**Created**: 2026-01-29
**Status**: Draft → Ready for Dev → In Progress → Complete
**QA Priority**: 🔴 CRITICAL
