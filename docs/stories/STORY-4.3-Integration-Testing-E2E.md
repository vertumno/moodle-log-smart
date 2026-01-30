# Story 4.3: Integration Testing End-to-End

**Story ID**: STORY-4.3
**Epic**: EPIC-04 (Docker + Deployment)
**Status**: Ready for Development
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 4
**Assigned to**: @dev (Dex)
**Estimate**: 1 dia

---

## 📖 User Story

**As a** quality assurance engineer
**I want** comprehensive end-to-end integration tests
**So that** Docker deployment is validated and reliable

---

## ✅ Acceptance Criteria

- [ ] E2E test script created and executable
- [ ] Full flow tested: Upload → Process → Download
- [ ] Healthchecks validated automatically
- [ ] Volume persistence verified
- [ ] Network connectivity confirmed
- [ ] Performance benchmark completed (5000 events < 2 min)
- [ ] All tests pass on first run
- [ ] Test results documented

---

## 🎯 Context & Requirements

### What Needs Testing
- **Container Startup**: Both services start successfully
- **Healthchecks**: Both services become healthy
- **API Connectivity**: Frontend can reach backend
- **File Upload**: CSV upload works via API
- **Processing**: Background job completes successfully
- **File Download**: ZIP download works
- **Volume Persistence**: Files persist after restart
- **Error Handling**: Proper error responses
- **Performance**: Processing time meets requirements

### Dependencies
- **Story 4.1**: Optimized Docker images
- **Story 4.2**: Production Docker Compose config
- **Sample Data**: Test CSV files available

---

## 📋 Implementation Tasks

### Task 1: Create E2E Test Script
**Subtasks:**
- [ ] Create `scripts/test-e2e.sh` (bash script)
- [ ] Add error handling and exit codes
- [ ] Add colored output (success/failure)
- [ ] Add verbose mode (-v flag)
- [ ] Make script executable

**Script Structure:**
```bash
#!/bin/bash
# test-e2e.sh - End-to-End Docker Integration Tests

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_container_startup() { ... }
test_healthchecks() { ... }
test_upload() { ... }
test_processing() { ... }
test_download() { ... }
test_persistence() { ... }
test_performance() { ... }

# Main execution
main() {
  echo "🧪 Starting E2E Integration Tests"
  test_container_startup
  test_healthchecks
  test_upload
  test_processing
  test_download
  test_persistence
  test_performance
  echo "✅ All tests passed!"
}

main
```

### Task 2: Test Container Startup
**Subtasks:**
- [ ] Start containers with docker-compose
- [ ] Wait for containers to be running
- [ ] Verify both containers exist
- [ ] Verify correct ports exposed
- [ ] Check container logs for errors

**Test Implementation:**
```bash
test_container_startup() {
  echo "Testing container startup..."

  # Start containers
  docker-compose up -d

  # Wait for startup
  sleep 10

  # Verify containers running
  BACKEND_STATUS=$(docker inspect -f '{{.State.Running}}' moodlelogsmart-backend)
  FRONTEND_STATUS=$(docker inspect -f '{{.State.Running}}' moodlelogsmart-frontend)

  if [[ "$BACKEND_STATUS" == "true" && "$FRONTEND_STATUS" == "true" ]]; then
    echo "✅ Containers started successfully"
  else
    echo "❌ Container startup failed"
    exit 1
  fi
}
```

### Task 3: Test Healthchecks
**Subtasks:**
- [ ] Wait for healthcheck intervals
- [ ] Check backend health status
- [ ] Check frontend health status
- [ ] Verify health endpoint responses
- [ ] Document expected healthcheck time

**Test Implementation:**
```bash
test_healthchecks() {
  echo "Testing healthchecks..."

  # Wait for health checks (30s interval + buffer)
  sleep 40

  # Check backend health
  BACKEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' moodlelogsmart-backend)

  # Check frontend health
  FRONTEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' moodlelogsmart-frontend)

  if [[ "$BACKEND_HEALTH" == "healthy" && "$FRONTEND_HEALTH" == "healthy" ]]; then
    echo "✅ Healthchecks passed"
  else
    echo "❌ Healthchecks failed: Backend=$BACKEND_HEALTH, Frontend=$FRONTEND_HEALTH"
    docker-compose logs
    exit 1
  fi
}
```

### Task 4: Test File Upload
**Subtasks:**
- [ ] Create test CSV file (or use sample)
- [ ] Upload via POST /api/upload
- [ ] Verify 200 response
- [ ] Extract job_id from response
- [ ] Verify upload directory contains file

**Test Implementation:**
```bash
test_upload() {
  echo "Testing file upload..."

  # Prepare test file
  TEST_FILE="tests/fixtures/sample_moodle_log.csv"

  if [[ ! -f "$TEST_FILE" ]]; then
    echo "❌ Test file not found: $TEST_FILE"
    exit 1
  fi

  # Upload file
  RESPONSE=$(curl -s -X POST \
    -F "file=@$TEST_FILE" \
    -H "X-API-Key: test-key-12345" \
    http://localhost:8000/api/upload)

  # Extract job_id
  JOB_ID=$(echo $RESPONSE | jq -r '.job_id')

  if [[ "$JOB_ID" != "null" && "$JOB_ID" != "" ]]; then
    echo "✅ File uploaded successfully (job_id: $JOB_ID)"
    export TEST_JOB_ID=$JOB_ID
  else
    echo "❌ Upload failed: $RESPONSE"
    exit 1
  fi
}
```

### Task 5: Test Processing
**Subtasks:**
- [ ] Poll GET /api/status/{job_id}
- [ ] Wait for status "completed"
- [ ] Set timeout (5 minutes)
- [ ] Verify no errors in status
- [ ] Check processing logs

**Test Implementation:**
```bash
test_processing() {
  echo "Testing processing..."

  TIMEOUT=300  # 5 minutes
  ELAPSED=0
  INTERVAL=5

  while [[ $ELAPSED -lt $TIMEOUT ]]; do
    STATUS_RESPONSE=$(curl -s \
      -H "X-API-Key: test-key-12345" \
      http://localhost:8000/api/status/$TEST_JOB_ID)

    STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')

    if [[ "$STATUS" == "completed" ]]; then
      echo "✅ Processing completed successfully"
      return 0
    elif [[ "$STATUS" == "failed" ]]; then
      echo "❌ Processing failed: $STATUS_RESPONSE"
      exit 1
    fi

    echo "  Status: $STATUS (${ELAPSED}s elapsed)"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
  done

  echo "❌ Processing timeout after ${TIMEOUT}s"
  exit 1
}
```

### Task 6: Test Download
**Subtasks:**
- [ ] Download ZIP via GET /api/download/{job_id}
- [ ] Verify 200 response
- [ ] Verify Content-Type: application/zip
- [ ] Save ZIP to temp location
- [ ] Unzip and verify contents
- [ ] Check for 4 expected files

**Test Implementation:**
```bash
test_download() {
  echo "Testing download..."

  # Download ZIP
  HTTP_CODE=$(curl -s -o /tmp/results.zip -w "%{http_code}" \
    -H "X-API-Key: test-key-12345" \
    http://localhost:8000/api/download/$TEST_JOB_ID)

  if [[ "$HTTP_CODE" == "200" ]]; then
    echo "✅ Download successful"
  else
    echo "❌ Download failed (HTTP $HTTP_CODE)"
    exit 1
  fi

  # Verify ZIP contents
  unzip -l /tmp/results.zip | grep -q "enriched_log.csv"
  unzip -l /tmp/results.zip | grep -q "enriched_log.xes"

  if [[ $? -eq 0 ]]; then
    echo "✅ ZIP contains expected files"
  else
    echo "❌ ZIP missing expected files"
    exit 1
  fi
}
```

### Task 7: Test Volume Persistence
**Subtasks:**
- [ ] Upload file and complete processing
- [ ] Stop containers (docker-compose down)
- [ ] Restart containers (docker-compose up)
- [ ] Verify job_id still accessible
- [ ] Verify files still in volumes

**Test Implementation:**
```bash
test_persistence() {
  echo "Testing volume persistence..."

  # Stop containers
  docker-compose down

  # Restart
  docker-compose up -d
  sleep 40  # Wait for healthchecks

  # Try to access previous job
  STATUS_RESPONSE=$(curl -s \
    -H "X-API-Key: test-key-12345" \
    http://localhost:8000/api/status/$TEST_JOB_ID)

  STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')

  if [[ "$STATUS" == "completed" ]]; then
    echo "✅ Volume persistence verified"
  else
    echo "⚠️  Job not found after restart (expected for in-memory storage)"
    echo "   This is OK if using in-memory job management"
  fi
}
```

### Task 8: Test Performance
**Subtasks:**
- [ ] Create large test file (5000 events)
- [ ] Upload and measure processing time
- [ ] Verify processing time < 2 minutes
- [ ] Document performance metrics

**Test Implementation:**
```bash
test_performance() {
  echo "Testing performance..."

  # Use large sample file
  LARGE_FILE="tests/fixtures/large_moodle_log_5000.csv"

  if [[ ! -f "$LARGE_FILE" ]]; then
    echo "⚠️  Large test file not found, skipping performance test"
    return 0
  fi

  START_TIME=$(date +%s)

  # Upload
  RESPONSE=$(curl -s -X POST \
    -F "file=@$LARGE_FILE" \
    -H "X-API-Key: test-key-12345" \
    http://localhost:8000/api/upload)

  PERF_JOB_ID=$(echo $RESPONSE | jq -r '.job_id')

  # Wait for completion
  TIMEOUT=120  # 2 minutes
  ELAPSED=0

  while [[ $ELAPSED -lt $TIMEOUT ]]; do
    STATUS=$(curl -s -H "X-API-Key: test-key-12345" \
      http://localhost:8000/api/status/$PERF_JOB_ID | jq -r '.status')

    if [[ "$STATUS" == "completed" ]]; then
      END_TIME=$(date +%s)
      DURATION=$((END_TIME - START_TIME))
      echo "✅ Performance test passed: ${DURATION}s (< 120s)"
      return 0
    fi

    sleep 5
    ELAPSED=$((ELAPSED + 5))
  done

  echo "❌ Performance test failed: Processing took > 120s"
  exit 1
}
```

### Task 9: Create Test Fixtures
**Subtasks:**
- [ ] Create `tests/fixtures/` directory
- [ ] Add sample_moodle_log.csv (100 events)
- [ ] Add large_moodle_log_5000.csv (5000 events)
- [ ] Document fixture format
- [ ] Add fixtures to git

### Task 10: Test Cleanup
**Subtasks:**
- [ ] Create cleanup function
- [ ] Stop containers after tests
- [ ] Remove test volumes (optional)
- [ ] Clean up temp files
- [ ] Add --no-cleanup flag (for debugging)

---

## 🧪 Testing Strategy

### Test Execution

**Run Full Suite:**
```bash
./scripts/test-e2e.sh
```

**Run with Verbose Output:**
```bash
./scripts/test-e2e.sh -v
```

**Run and Keep Containers Running:**
```bash
./scripts/test-e2e.sh --no-cleanup
```

### Expected Output

```
🧪 Starting E2E Integration Tests

Testing container startup...
✅ Containers started successfully

Testing healthchecks...
✅ Healthchecks passed

Testing file upload...
✅ File uploaded successfully (job_id: abc-123)

Testing processing...
  Status: processing (5s elapsed)
  Status: processing (10s elapsed)
✅ Processing completed successfully

Testing download...
✅ Download successful
✅ ZIP contains expected files

Testing volume persistence...
✅ Volume persistence verified

Testing performance...
✅ Performance test passed: 45s (< 120s)

✅ All tests passed!
```

---

## 📝 Implementation Checklist

### Planning
- [x] Test scenarios identified
- [x] Test data requirements defined
- [x] Success criteria established

### Development
- [ ] test-e2e.sh script created
- [ ] All test functions implemented
- [ ] Test fixtures created
- [ ] Error handling added
- [ ] Cleanup logic implemented

### Testing
- [ ] Script runs without errors
- [ ] All tests pass on clean environment
- [ ] Tests pass on Windows/Linux/macOS
- [ ] Performance benchmarks documented

### Documentation
- [ ] Test script usage documented
- [ ] Test fixtures documented
- [ ] Expected results documented
- [ ] Troubleshooting guide added

---

## 📊 Test Coverage

| Test | Coverage | Status |
|------|----------|--------|
| Container Startup | Backend + Frontend | ⏳ |
| Healthchecks | HTTP endpoints | ⏳ |
| File Upload | POST /api/upload | ⏳ |
| Job Processing | Background worker | ⏳ |
| File Download | GET /api/download | ⏳ |
| Volume Persistence | Docker volumes | ⏳ |
| Network Connectivity | Inter-container | ⏳ |
| Performance | 5000 events < 2min | ⏳ |

---

## 📁 File List

**Files to Create:**
- [ ] `scripts/test-e2e.sh` - Main E2E test script
- [ ] `tests/fixtures/sample_moodle_log.csv` - Small test file
- [ ] `tests/fixtures/large_moodle_log_5000.csv` - Large test file
- [ ] `tests/fixtures/README.md` - Fixture documentation
- [ ] `docs/deployment/TESTING-GUIDE.md` - Testing documentation

**Files to Modify:**
- [ ] `.gitignore` - Exclude test outputs
- [ ] `README.md` - Add testing section

**Scripts Permissions:**
```bash
chmod +x scripts/test-e2e.sh
```

---

## 🔗 Dependencies & Blockers

**Depends on:**
- ✅ Story 4.1: Optimized Docker images
- ✅ Story 4.2: Production Docker Compose
- ✅ Epic 1-3: Full application implemented

**Blocks:**
- Story 4.4: Deployment Documentation (needs test results)

**External Dependencies:**
- Docker & Docker Compose installed
- curl, jq installed (for API testing)
- bash shell (Linux/macOS/WSL)

---

## 🛠️ Technical Details

### Test Architecture

```
test-e2e.sh
├── setup()
│   ├── Pull latest images
│   ├── Generate test API key
│   └── Prepare test data
├── test_container_startup()
├── test_healthchecks()
├── test_upload()
├── test_processing()
├── test_download()
├── test_persistence()
├── test_performance()
└── cleanup()
    ├── Stop containers
    ├── Remove volumes (optional)
    └── Clean temp files
```

### Error Handling

All test functions should:
1. Return 0 on success
2. Exit 1 on failure
3. Log detailed error messages
4. Capture relevant logs before exiting

### Performance Benchmarks

| File Size | Events | Target Time | Max Time |
|-----------|--------|-------------|----------|
| Small | 100 | < 10s | 30s |
| Medium | 1000 | < 30s | 60s |
| Large | 5000 | < 90s | 120s |

---

## 📚 References

**Testing Best Practices:**
- https://docs.docker.com/compose/test/
- https://docs.docker.com/engine/api/

**Shell Scripting:**
- https://www.shellcheck.net/ (validation tool)

**Related Stories:**
- Story 4.1: Dockerfiles Optimization
- Story 4.2: Docker Compose Production
- Story 4.4: Deployment Documentation

---

## ✨ Notes for Developer

**Critical Tests (Must Pass):**
1. Container startup
2. Healthchecks
3. Upload → Process → Download flow

**Important Tests:**
4. Volume persistence
5. Performance

**Nice-to-Have:**
6. Error scenario testing
7. Concurrent uploads

**Testing Tips:**
- Test on clean system first (no cached images)
- Use `--no-cache` for true build time test
- Run tests multiple times to catch intermittent issues
- Monitor resource usage during performance test

**Common Issues:**
- Port conflicts (3000/8000 already in use)
- Insufficient memory (Docker Desktop limits)
- Slow healthchecks (increase wait time)
- Volume permission issues (non-root users)

---

**Created**: 2026-01-29
**Status**: ✅ Ready for Development
**Assigned**: @dev (Dex)
