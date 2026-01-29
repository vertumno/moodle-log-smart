# Story 2.4: Job Management & Error Handling

**Story ID**: STORY-2.4
**Epic**: EPIC-02 (API Layer)
**Status**: Ready for Review
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 2
**Assigned to**: @dev (Dex)
**Estimate**: 0.5 dia

---

## 📖 User Story

**As a** sistema
**I want** gerenciar jobs em memória
**So that** múltiplos usuários possam processar logs simultaneamente

---

## ✅ Acceptance Criteria

- [x] Dict em memória: `{job_id: JobState}`
- [x] JobState contém: {status, progress, result_path, error, timestamps}
- [x] Job lifecycle: create → processing → completed/failed
- [x] Progress tracking (0-100%)
- [x] Error messages são user-friendly
- [x] Background processing support

---

## 🎯 Context & Requirements

### Dependencies
- **FastAPI**: Background tasks
- **UUID**: For unique job IDs
- **Dataclasses**: For Job model
- **Logging**: For debugging and monitoring

### Technical Details

**JobManager Class**:
```python
class JobManager:
    jobs: Dict[str, Job]  # In-memory storage

    def create_job() -> str
    def get_job(job_id) -> Optional[Job]
    def update_progress(job_id, progress)
    def mark_completed(job_id, output_file)
    def mark_failed(job_id, error)
    def cleanup_job(job_id)
```

**Job Dataclass**:
```python
@dataclass
class Job:
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: int  # 0-100
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    input_file: Optional[Path]
    output_file: Optional[Path]
```

**Job Lifecycle**:
1. **Created**: New job → status="processing", progress=0
2. **Processing**: Background task updates progress (10, 20, ..., 95)
3. **Completed**: Success → status="completed", progress=100, output_file set
4. **Failed**: Error → status="failed", error message set

---

## 📋 Implementation Tasks

### Task 1: Create Job Dataclass
**Subtasks:**
- [x] Define Job dataclass with all fields
- [x] Use dataclass decorator for clean model
- [x] Add type hints for all fields
- [x] Set sensible defaults (status="processing", progress=0)
- [x] Use datetime for timestamps

### Task 2: Implement JobManager Class
**Subtasks:**
- [x] Create JobManager class
- [x] Initialize jobs dict in __init__
- [x] Implement create_job() with UUID generation
- [x] Implement get_job() for retrieval
- [x] Implement update_progress() with bounds checking
- [x] Implement mark_completed() with timestamp
- [x] Implement mark_failed() with error message
- [x] Add logging for all operations

### Task 3: Global Instance Management
**Subtasks:**
- [x] Create global _job_manager variable
- [x] Implement get_job_manager() factory function
- [x] Ensure singleton pattern (one instance)
- [x] Thread-safe access (FastAPI handles this)

### Task 4: File Management
**Subtasks:**
- [x] Add set_input_file() method
- [x] Add cleanup_job() method
- [x] Delete input file after processing
- [x] Keep output file for download
- [x] Log file operations

### Task 5: Integration with API Endpoints
**Subtasks:**
- [x] Use job_manager in upload endpoint
- [x] Use job_manager in status endpoint
- [x] Use job_manager in download endpoint
- [x] Update progress during processing
- [x] Handle errors gracefully

### Task 6: Error Handling
**Subtasks:**
- [x] User-friendly error messages
- [x] Log detailed errors for debugging
- [x] Prevent raw exceptions from leaking
- [x] HTTP status codes match errors
- [x] Mark jobs as failed on exceptions

---

## 🧪 Testing Strategy

**Unit Tests**:

1. **Test: Create Job**
   - Call create_job()
   - Verify unique UUID returned
   - Verify job in manager.jobs
   - Verify default status="processing", progress=0

2. **Test: Get Job**
   - Create job → get job_id
   - Call get_job(job_id)
   - Verify returns Job object
   - Call get_job("invalid") → None

3. **Test: Update Progress**
   - Create job
   - Update progress to 50
   - Verify job.progress == 50
   - Update to -10 → clamps to 0
   - Update to 150 → clamps to 100

4. **Test: Mark Completed**
   - Create job
   - Mark completed with output_file
   - Verify status="completed"
   - Verify progress=100
   - Verify completed_at set
   - Verify output_file stored

5. **Test: Mark Failed**
   - Create job
   - Mark failed with error message
   - Verify status="failed"
   - Verify error message stored
   - Verify completed_at set

6. **Test: File Management**
   - Create job with input file
   - Verify set_input_file() stores path
   - Call cleanup_job()
   - Verify input file deleted (if exists)

---

## 🏗️ Architecture

### In-Memory Storage
- Simple dict: `{job_id: Job}`
- Fast lookups O(1)
- No persistence (jobs lost on restart)
- Suitable for MVP (future: Redis/database)

### Thread Safety
- FastAPI uses async/await (single-threaded event loop)
- No need for locks in current implementation
- Future: Add locks if switching to threads

### Scalability Considerations
- **Current**: Single-process, in-memory
- **Future**: Redis for multi-process
- **Future**: Database for persistence
- **Future**: Message queue for distributed processing

---

## 📝 Dev Agent Record

### Checklist
- [x] Task 1: Job dataclass created
- [x] Task 2: JobManager class implemented
- [x] Task 3: Global instance management
- [x] Task 4: File management
- [x] Task 5: API integration
- [x] Task 6: Error handling

### Debug Log
- Implemented in `backend/src/moodlelogsmart/api/job_manager.py`
- Job dataclass: lines 14-25
- JobManager class: lines 27-126
- Global factory: lines 128-142
- Integration in `main.py` throughout upload/status/download
- Progress updates in process_job: lines 185-277

### Completion Notes
**Implementation Details:**
- JobManager uses dict for O(1) lookups
- Job dataclass provides type safety
- Singleton pattern via get_job_manager()
- Progress clamped to [0, 100] range
- Timestamps track creation and completion
- File paths tracked for cleanup

**Quality Checks:**
- ✅ Type hints on all methods
- ✅ Docstrings for all public methods
- ✅ Logging for debugging
- ✅ Progress bounds checking
- ✅ Clean dataclass model

**Acceptance Criteria Met:**
- ✅ In-memory dict storage
- ✅ Complete JobState model
- ✅ Full job lifecycle support
- ✅ Progress tracking 0-100%
- ✅ User-friendly errors
- ✅ Background processing integrated

### File List
**Files Created:**
- [x] `backend/src/moodlelogsmart/api/job_manager.py` (142 lines)
- [x] `backend/src/moodlelogsmart/api/models.py` (43 lines)

**Files Modified:**
- [x] `backend/src/moodlelogsmart/main.py` (integrated JobManager)

**Files to Delete:**
- None

### Change Log
- Story 2.4 implemented as part of initial API development
- JobManager created to support async processing
- Job dataclass provides clean state model
- Integration with all 3 API endpoints
- Implemented in commit 8238ca1

---

## 📚 References

**Epic 2**: docs/epics/EPIC-02-API-Layer.md
**Story 2.1**: Upload Endpoint (uses JobManager)
**Story 2.2**: Status Endpoint (uses JobManager)
**Story 2.3**: Download Endpoint (uses JobManager)
**Python Dataclasses**: https://docs.python.org/3/library/dataclasses.html

---

## ✨ Notes for Developer

- In-memory storage suitable for MVP
- Jobs lost on server restart (acceptable for now)
- Future: Add Redis for persistence and multi-process support
- Future: Add cleanup task for old completed jobs
- Future: Add timeout detection for stuck jobs
- Consider job retention policy (delete after 1 hour?)

---

**Created**: 2026-01-29
**Status**: ✅ Ready for Review
**Completed**: 2026-01-29 (retroactive documentation)
