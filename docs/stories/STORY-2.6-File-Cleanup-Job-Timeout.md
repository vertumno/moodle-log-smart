# Story 2.6: File Cleanup & Job Timeout

**Story ID**: STORY-2.6
**Epic**: EPIC-02 (API Layer - Reliability)
**Status**: Draft
**Priority**: P0 (Critical - Resource Management)
**Sprint**: Sprint 2 (Security Hardening)
**Assigned to**: @dev (Dex)
**Estimate**: 0.5 dia

---

## 📖 User Story

**As a** system administrator
**I want** automatic cleanup of old files and stuck jobs
**So that** disk space doesn't fill up and jobs don't hang forever

---

## ✅ Acceptance Criteria

- [ ] Completed jobs cleaned up after 24 hours
- [ ] Failed jobs cleaned up after 1 hour
- [ ] Processing jobs timeout after 10 minutes
- [ ] Cleanup runs automatically every hour
- [ ] Input files deleted immediately after processing
- [ ] Output files deleted after retention period
- [ ] Stuck jobs marked as failed
- [ ] Cleanup logged for monitoring

---

## 🎯 Context & Requirements

### Issues Addressed
From QA Review (EPIC-02-QA-GATE.md):
- 🟡 **File Accumulation** (Risk Score: 6/10) - Disk will fill
- 🟡 **Job Timeout** (Risk Score: 5/10) - Stuck jobs never fail

### Technical Approach
- Background task running every hour
- TTL-based cleanup (time-to-live)
- Timeout detection during processing
- Graceful handling (no data loss)

---

## 📋 Implementation Tasks

### Task 1: Job Timeout Implementation
**Subtasks:**
- [ ] Wrap `process_job()` with timeout
- [ ] Set timeout to 10 minutes (600s)
- [ ] Mark job as failed on timeout
- [ ] Log timeout events
- [ ] Test timeout scenario

### Task 2: Cleanup Background Task
**Subtasks:**
- [ ] Create `cleanup_old_jobs()` async function
- [ ] Run cleanup every hour (3600s interval)
- [ ] Start cleanup on app startup
- [ ] Stop cleanup on app shutdown
- [ ] Log cleanup operations

### Task 3: TTL Logic
**Subtasks:**
- [ ] Define retention periods (configurable)
- [ ] Check job completion timestamp
- [ ] Delete files if past TTL
- [ ] Remove job from JobManager
- [ ] Handle file deletion errors gracefully

### Task 4: Immediate Input Cleanup
**Subtasks:**
- [ ] Delete input file after processing starts
- [ ] Keep output file for download
- [ ] Handle errors if file doesn't exist
- [ ] Log cleanup operations

### Task 5: Configuration
**Subtasks:**
- [ ] Add environment variables for TTLs
- [ ] Document configuration in README
- [ ] Provide sensible defaults
- [ ] Validate configuration on startup

### Task 6: Testing
**Subtasks:**
- [ ] Test timeout detection
- [ ] Test TTL cleanup
- [ ] Test cleanup interval
- [ ] Test file deletion
- [ ] Test error handling

---

## 🔧 Implementation Details

### Job Timeout

**File**: `backend/src/moodlelogsmart/main.py`

```python
import asyncio

async def process_job_with_timeout(job_id: str, input_file: str) -> None:
    """Process job with timeout protection.

    Args:
        job_id: Job identifier
        input_file: Path to input CSV

    Timeout: 10 minutes (configurable)
    """
    timeout = int(os.getenv("JOB_TIMEOUT_SECONDS", "600"))  # 10 min

    try:
        await asyncio.wait_for(
            process_job(job_id, input_file),
            timeout=float(timeout)
        )
    except asyncio.TimeoutError:
        logger.error(f"Job {job_id} timed out after {timeout}s")
        job_manager.mark_failed(
            job_id,
            f"Processing timeout ({timeout // 60} minutes)"
        )
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        job_manager.mark_failed(job_id, str(e))


# Update upload endpoint to use timeout wrapper
@app.post("/api/upload")
async def upload_csv(...):
    # ... validation code ...

    # Start background processing WITH timeout
    background_tasks.add_task(
        process_job_with_timeout,  # Changed from process_job
        job_id,
        str(temp_input)
    )
```

---

### Cleanup Background Task

**File**: `backend/src/moodlelogsmart/main.py`

```python
from datetime import datetime, timedelta

# Cleanup configuration
CLEANUP_INTERVAL = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "3600"))  # 1 hour
TTL_COMPLETED = int(os.getenv("TTL_COMPLETED_HOURS", "24"))  # 24 hours
TTL_FAILED = int(os.getenv("TTL_FAILED_HOURS", "1"))  # 1 hour


async def cleanup_old_jobs() -> None:
    """Periodic cleanup of old jobs and files.

    Runs every hour. Cleans up:
    - Completed jobs older than 24 hours
    - Failed jobs older than 1 hour
    - Associated files
    """
    while True:
        try:
            await asyncio.sleep(CLEANUP_INTERVAL)

            now = datetime.now()
            jobs_to_clean = []

            for job_id, job in job_manager.jobs.items():
                if not job.completed_at:
                    continue  # Skip active jobs

                age = now - job.completed_at

                # Check if TTL expired
                should_clean = False
                if job.status == "completed" and age > timedelta(hours=TTL_COMPLETED):
                    should_clean = True
                    reason = f"Completed job older than {TTL_COMPLETED}h"
                elif job.status == "failed" and age > timedelta(hours=TTL_FAILED):
                    should_clean = True
                    reason = f"Failed job older than {TTL_FAILED}h"

                if should_clean:
                    jobs_to_clean.append((job_id, reason))

            # Clean up identified jobs
            for job_id, reason in jobs_to_clean:
                logger.info(f"Cleaning up job {job_id}: {reason}")
                job_manager.cleanup_job(job_id)
                del job_manager.jobs[job_id]

            if jobs_to_clean:
                logger.info(f"Cleanup: Removed {len(jobs_to_clean)} old jobs")

        except Exception as e:
            logger.error(f"Cleanup task error: {e}", exc_info=True)


# Start cleanup on startup
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("MoodleLogSmart API starting up")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    # Start cleanup background task
    asyncio.create_task(cleanup_old_jobs())
    logger.info(f"Cleanup task started (interval: {CLEANUP_INTERVAL}s)")
```

---

### Enhanced JobManager Cleanup

**File**: `backend/src/moodlelogsmart/api/job_manager.py`

```python
def cleanup_job(self, job_id: str) -> None:
    """Clean up job files and remove from memory.

    Args:
        job_id: Job identifier
    """
    job = self.get_job(job_id)
    if not job:
        return

    files_deleted = 0

    # Delete input file
    if job.input_file and job.input_file.exists():
        try:
            job.input_file.unlink()
            files_deleted += 1
            logger.debug(f"Deleted input file: {job.input_file}")
        except Exception as e:
            logger.warning(f"Failed to delete input file: {e}")

    # Delete output file (after retention period)
    if job.output_file and job.output_file.exists():
        try:
            job.output_file.unlink()
            files_deleted += 1
            logger.debug(f"Deleted output file: {job.output_file}")
        except Exception as e:
            logger.warning(f"Failed to delete output file: {e}")

    # Delete output directory if exists
    output_dir = Path(tempfile.gettempdir()) / "moodlelogsmart" / f"{job_id}_output"
    if output_dir.exists():
        try:
            import shutil
            shutil.rmtree(output_dir)
            logger.debug(f"Deleted output directory: {output_dir}")
        except Exception as e:
            logger.warning(f"Failed to delete output directory: {e}")

    logger.info(f"Job {job_id} cleanup complete ({files_deleted} files deleted)")
```

---

### Immediate Input File Cleanup

**File**: `backend/src/moodlelogsmart/main.py`

```python
async def process_job(job_id: str, input_file: str) -> None:
    """Process CSV file in background."""
    input_path = Path(input_file)

    try:
        logger.info(f"Job {job_id}: Starting processing")
        job_manager.update_progress(job_id, 10)

        # ... processing steps ...

        job_manager.update_progress(job_id, 95)

        # Mark job as completed
        job_manager.mark_completed(job_id, zip_path)
        logger.info(f"Job {job_id}: Processing completed successfully")

    except Exception as e:
        logger.error(f"Job {job_id}: Processing failed: {str(e)}", exc_info=True)
        job_manager.mark_failed(job_id, str(e))

    finally:
        # ALWAYS delete input file after processing (success or failure)
        if input_path.exists():
            try:
                input_path.unlink()
                logger.debug(f"Job {job_id}: Deleted input file")
            except Exception as e:
                logger.warning(f"Job {job_id}: Failed to delete input: {e}")
```

---

## 🧪 Testing Strategy

### Test: Job Timeout
```python
@pytest.mark.asyncio
async def test_job_timeout():
    """Test job timeout detection."""
    import asyncio

    # Create a job that takes 15 minutes
    async def slow_job(job_id, input_file):
        await asyncio.sleep(900)  # 15 minutes

    # Mock with 1 second timeout
    with patch.dict(os.environ, {"JOB_TIMEOUT_SECONDS": "1"}):
        job_id = "test-job"
        await process_job_with_timeout(job_id, "test.csv")

        # Verify job marked as failed with timeout
        job = job_manager.get_job(job_id)
        assert job.status == "failed"
        assert "timeout" in job.error.lower()
```

### Test: TTL Cleanup
```python
def test_cleanup_old_completed_job():
    """Test cleanup of old completed job."""
    from datetime import datetime, timedelta

    # Create completed job 25 hours ago
    job_id = job_manager.create_job()
    job_manager.mark_completed(job_id, Path("/tmp/test.zip"))

    job = job_manager.get_job(job_id)
    job.completed_at = datetime.now() - timedelta(hours=25)

    # Run cleanup
    asyncio.run(cleanup_old_jobs())

    # Verify job removed
    assert job_manager.get_job(job_id) is None
```

### Test: Failed Job Cleanup
```python
def test_cleanup_old_failed_job():
    """Test cleanup of old failed job."""
    # Create failed job 2 hours ago
    job_id = job_manager.create_job()
    job_manager.mark_failed(job_id, "Test error")

    job = job_manager.get_job(job_id)
    job.completed_at = datetime.now() - timedelta(hours=2)

    # Run cleanup
    asyncio.run(cleanup_old_jobs())

    # Verify job removed
    assert job_manager.get_job(job_id) is None
```

---

## 📝 Environment Configuration

### .env.example
```bash
# Job Processing
JOB_TIMEOUT_SECONDS=600  # 10 minutes

# File Cleanup
CLEANUP_INTERVAL_SECONDS=3600  # 1 hour
TTL_COMPLETED_HOURS=24  # Keep completed jobs 24h
TTL_FAILED_HOURS=1  # Keep failed jobs 1h
```

---

## 📊 Monitoring

### Metrics to Track
- Jobs cleaned up per hour
- Disk space freed
- Timeout events count
- Average job duration
- Active jobs count

### Logging
```python
# Add structured logging
logger.info(
    "Cleanup completed",
    extra={
        "jobs_cleaned": len(jobs_to_clean),
        "disk_freed_mb": disk_freed / (1024 * 1024),
        "duration_ms": duration * 1000
    }
)
```

---

## 📝 Dev Agent Record

### Checklist
- [ ] Task 1: Job timeout implemented
- [ ] Task 2: Cleanup background task created
- [ ] Task 3: TTL logic working
- [ ] Task 4: Immediate input cleanup
- [ ] Task 5: Configuration added
- [ ] Task 6: Tests passing

### Debug Log
[Will be updated during development]

### Completion Notes
[Will be updated upon completion]

### File List
**Files to Create:**
- [ ] None (all modifications)

**Files to Modify:**
- [ ] `backend/src/moodlelogsmart/main.py` (timeout + cleanup task)
- [ ] `backend/src/moodlelogsmart/api/job_manager.py` (enhanced cleanup)
- [ ] `backend/.env.example` (add config vars)
- [ ] `backend/tests/test_api.py` (add timeout/cleanup tests)
- [ ] `backend/README.md` (document cleanup behavior)

**Files to Delete:**
- [ ] None

### Change Log
[Will add commits during development]

---

## 📚 References

**QA Review**: docs/qa/gates/EPIC-02-QA-GATE.md
**File Accumulation Risk**: Score 6/10
**Job Timeout Risk**: Score 5/10

---

**Created**: 2026-01-29
**Status**: Draft → Ready for Dev → In Progress → Complete
**QA Priority**: 🔴 CRITICAL
