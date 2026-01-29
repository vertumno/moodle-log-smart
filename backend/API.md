# MoodleLogSmart API Documentation

## Overview

REST API for processing Moodle CSV logs and enriching them with Bloom's Taxonomy classification.

**Base URL**: `http://localhost:8000`
**API Version**: 0.1.0

---

## Running the API

### Development Server

```bash
cd backend
poetry install
poetry run uvicorn moodlelogsmart.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
poetry run uvicorn moodlelogsmart.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
docker build -t moodlelogsmart-api .
docker run -p 8000:8000 moodlelogsmart-api
```

---

## Health Check

**Endpoint**: `GET /health`

Check API availability.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

## Endpoints

### 1. Upload CSV File

**Endpoint**: `POST /api/upload`

Upload a Moodle CSV log file for processing.

**Request**:
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: CSV file (required, max 50MB)

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@logs/moodle_log.csv"
```

**Response** (200):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "File uploaded and processing started"
}
```

**Error Responses**:
- **400**: File validation failed
  ```json
  {
    "detail": "Only .csv files are allowed"
  }
  ```
- **413**: File too large (> 50MB)
  ```json
  {
    "detail": "File size exceeds 50MB limit"
  }
  ```
- **500**: Internal server error
  ```json
  {
    "detail": "Internal server error"
  }
  ```

---

### 2. Get Processing Status

**Endpoint**: `GET /api/status/{job_id}`

Check the processing status and progress of a job.

**Path Parameters**:
- `job_id`: Job identifier (from upload response)

**cURL Example**:
```bash
curl http://localhost:8000/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "error": null,
  "created_at": "2024-01-15T10:30:45.123456",
  "completed_at": null
}
```

**Status Values**:
- `processing`: Job is currently being processed
- `completed`: Job completed successfully
- `failed`: Job failed with error

**Progress**: 0-100 (percentage)

**Error Response**:
- **404**: Job not found
  ```json
  {
    "detail": "Job not found"
  }
  ```

---

### 3. Download Results

**Endpoint**: `GET /api/download/{job_id}`

Download processed results as ZIP file.

**Path Parameters**:
- `job_id`: Job identifier (from upload response)

**cURL Example**:
```bash
curl http://localhost:8000/api/download/550e8400-e29b-41d4-a716-446655440000 \
  --output results.zip
```

**Response** (200):
- **Content-Type**: `application/zip`
- **Body**: ZIP file containing:
  - `enriched_log.csv` - Full enriched log
  - `enriched_log.xes` - Full log in XES format (for process mining)
  - `enriched_log_bloom_only.csv` - Bloom-classified activities only
  - `enriched_log_bloom_only.xes` - Bloom activities in XES format

**Error Responses**:
- **404**: Job or file not found
  ```json
  {
    "detail": "Job not found"
  }
  ```
- **400**: Job not yet completed
  ```json
  {
    "detail": "Job status is processing"
  }
  ```

---

## Example Workflow

### Step 1: Upload File
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@moodle_log.csv" \
  -o response.json

# Extract job_id from response
job_id=$(jq -r '.job_id' response.json)
```

### Step 2: Poll Status
```bash
# Check status every 5 seconds until completed
while true; do
  status=$(curl http://localhost:8000/api/status/$job_id)
  progress=$(echo $status | jq '.progress')
  job_status=$(echo $status | jq -r '.status')

  echo "Progress: $progress% - Status: $job_status"

  if [ "$job_status" == "completed" ] || [ "$job_status" == "failed" ]; then
    break
  fi

  sleep 5
done
```

### Step 3: Download Results
```bash
curl http://localhost:8000/api/download/$job_id \
  --output results_$(date +%s).zip

# Extract ZIP
unzip results_*.zip
```

---

## CSV Input Format

### Required Columns
The input CSV must contain these columns (names detected automatically):
- **Time**: Event timestamp (various formats supported)
- **Event name**: Name of the event (e.g., "Course module viewed")
- **Component**: Component/module type (e.g., "File", "Assignment")
- **User full name**: Full name of the user

### Supported Formats

**Encoding**: Detected automatically
- UTF-8 (default)
- Latin-1 (ISO-8859-1)
- CP1252 (Windows)

**Delimiters**: Detected automatically
- `,` (comma)
- `;` (semicolon)
- `\t` (tab)
- `|` (pipe)

**Timestamp Formats**: Multiple formats supported
- `YYYY-MM-DD HH:MM:SS`
- `DD/MM/YY, HH:MM:SS`
- And 10+ other common formats

---

## Output Format

### CSV Output

Enriched CSV contains all input columns plus:

| Column | Description | Example |
|--------|-------------|---------|
| `activity_type` | Semantic activity type | `Study_P`, `Exercise_A` |
| `bloom_level` | Bloom's Taxonomy level | `Remember`, `Apply`, `Analyze` |

**Activity Types**:
- `Study_P`: Viewing learning materials (passive)
- `Study_A`: Completing readings (active)
- `Exercise_P`: Viewing exercises (passive)
- `Exercise_A`: Solving exercises (active)
- `Assess_P`: Viewing assessments (passive)
- `Assess_A`: Completing assessments (active)
- `Synthesize`: Creating new content
- `View`: General navigation
- `Feedback`: Receiving feedback
- `Interact`: Social interaction
- `Others`: Other events

**Bloom Levels**:
- `Remember`: Recognizing, recalling
- `Understand`: Interpreting, summarizing
- `Apply`: Executing, implementing
- `Analyze`: Differentiating, organizing
- `Evaluate`: Checking, critiquing
- `Create`: Generating, planning
- `N/A`: Non-pedagogical events

---

## XES Output

XES (eXtensible Event Stream) files for process mining tools:
- **ProM** (https://www.promtools.org/)
- **Disco** (https://www.discoprocess.com/)
- **Celonis** (https://www.celonis.com/)

Structure:
- **Traces**: Grouped by user
- **Events**: Timestamped activities with Bloom classification
- **Attributes**: Component type, Bloom level

---

## CORS Configuration

The API has CORS enabled for all origins in development:

```python
CORSMiddleware(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**: Restrict to specific domains:
```python
allow_origins=["https://yourdomain.com"]
```

---

## Limits & Constraints

| Parameter | Limit | Notes |
|-----------|-------|-------|
| File size | 50 MB | Configurable in code |
| Processing timeout | 10 minutes | Per job |
| Concurrent jobs | Unlimited (MVP) | In-memory, scales horizontally in future |
| Job retention | Until server restart | No persistence in MVP |

---

## Troubleshooting

### "Only .csv files are allowed"
Ensure your file has `.csv` extension. File type is checked by extension only.

### "File size exceeds 50MB"
Split your CSV into smaller files or increase limit in code:
```python
if file_size_mb > 50:  # Change 50 to desired size
```

### Job stays in "processing" state
Check server logs for errors:
```bash
docker logs container_name
# or
tail -f logs/api.log
```

### XES export fails
Ensure PM4Py is installed:
```bash
poetry add pm4py
```

---

## API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Testing

Run API tests:

```bash
# All tests
poetry run pytest tests/test_api.py -v

# With coverage
poetry run pytest tests/test_api.py --cov=moodlelogsmart
```

---

## Performance Notes

- **CSV Detection**: < 1 second
- **Column Mapping**: < 1 second
- **Data Cleaning**: Depends on file size
- **Rule Application**: ~0.5ms per event
- **Export**: ~1-2 seconds for 5000 events

**Typical Processing Time**:
- 1000 events: ~15-30 seconds
- 5000 events: ~60-120 seconds

---

*Last Updated: 2026-01-29*
*Version: 0.1.0*
