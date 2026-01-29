# Story 2.3: Endpoint de Download

**Story ID**: STORY-2.3
**Epic**: EPIC-02 (API Layer)
**Status**: Ready for Review
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 2
**Assigned to**: @dev (Dex)
**Estimate**: 1 dia

---

## 📖 User Story

**As a** frontend
**I want** baixar ZIP de resultados
**So that** usuário receba os arquivos processados

---

## ✅ Acceptance Criteria

- [x] GET `/api/download/{job_id}` retorna ZIP file
- [x] Content-Type: application/zip
- [x] Header: Content-Disposition com filename
- [x] Retorna 404 se job não existe
- [x] Retorna 400 se job não completou
- [x] Arquivo ZIP contém todos os resultados (CSV, XES, Bloom-only)

---

## 🎯 Context & Requirements

### Dependencies
- **Story 2.1**: Upload endpoint deve estar completo
- **Story 2.2**: Status endpoint deve estar completo
- **Story 2.4**: JobManager deve estar implementado
- **Epic 1**: Backend core para processar e gerar arquivos

### Technical Details

**Endpoint**: `GET /api/download/{job_id}`

**Response Headers**:
```
Content-Type: application/zip
Content-Disposition: attachment; filename=results_YYYYMMDD_HHMMSS.zip
```

**ZIP Contents**:
- `enriched_log.csv` - CSV enriquecido completo
- `enriched_log.xes` - XES format completo (se disponível)
- `enriched_log_bloom_only.csv` - Apenas eventos com Bloom
- `enriched_log_bloom_only.xes` - XES apenas Bloom (se disponível)

**Error Responses**:
- `404` - Job not found
- `400` - Job status is not "completed"
- `404` - Results file not found (após completed)

---

## 📋 Implementation Tasks

### Task 1: Implement Download Endpoint
**Subtasks:**
- [x] Create GET `/api/download/{job_id}` endpoint
- [x] Validate job exists (404 if not)
- [x] Validate job is completed (400 if not)
- [x] Validate output file exists (404 if not)
- [x] Return FileResponse with correct headers

### Task 2: Configure Response Headers
**Subtasks:**
- [x] Set Content-Type: application/zip
- [x] Set Content-Disposition with dynamic filename
- [x] Use job output_file name from JobManager

### Task 3: Error Handling
**Subtasks:**
- [x] Handle job not found (404)
- [x] Handle job not completed (400)
- [x] Handle file not found (404)
- [x] User-friendly error messages

### Task 4: Integration with JobManager
**Subtasks:**
- [x] Use job_manager.get_job() to retrieve job
- [x] Check job.status == "completed"
- [x] Use job.output_file for FileResponse
- [x] Verify file exists before serving

### Task 5: Testing
**Subtasks:**
- [x] Test download with non-existent job (404)
- [x] Test download before completion (400)
- [x] Test successful download (200)
- [x] Test file headers correct
- [x] Test ZIP content validity

---

## 🧪 Testing Strategy

**API Tests**:

1. **Test: Download Non-Existent Job**
   - GET `/api/download/invalid-uuid`
   - Expect: 404 Not Found
   - Error message: "Job not found"

2. **Test: Download Before Completion**
   - Upload CSV → Get job_id
   - Immediately GET `/api/download/{job_id}`
   - Expect: 400 Bad Request
   - Error message: "Job status is processing"

3. **Test: Successful Download**
   - Upload CSV → Wait for completion
   - GET `/api/download/{job_id}`
   - Expect: 200 OK
   - Content-Type: application/zip
   - Content-Disposition header present
   - ZIP file contains expected files

4. **Test: Download Missing File**
   - Mock job with completed status but no output_file
   - GET `/api/download/{job_id}`
   - Expect: 404 Not Found
   - Error message: "Results file not found"

---

## 📝 Dev Agent Record

### Checklist
- [x] Task 1: Download endpoint implemented
- [x] Task 2: Response headers configured
- [x] Task 3: Error handling complete
- [x] Task 4: JobManager integration working
- [x] Task 5: Tests passing

### Debug Log
- Implemented in `backend/src/moodlelogsmart/main.py:146-173`
- Uses FastAPI's FileResponse for efficient file serving
- JobManager tracks output_file path
- ZIP created in process_job() at line 262-272
- Tests in `backend/tests/test_api.py:100-117`

### Completion Notes
**Implementation Details:**
- Endpoint location: `main.py` lines 146-173
- Returns FileResponse with path, media_type, and filename
- Validates job exists, is completed, and file exists
- Error handling returns appropriate HTTP status codes
- Integration with JobManager for state management

**Quality Checks:**
- ✅ Code follows FastAPI best practices
- ✅ Error handling comprehensive
- ✅ HTTP status codes correct
- ✅ File serving efficient (FileResponse)
- ✅ Tests cover all scenarios

**Acceptance Criteria Met:**
- ✅ GET endpoint implemented
- ✅ Returns application/zip
- ✅ Filename in Content-Disposition
- ✅ 404 for non-existent job
- ✅ 400 for incomplete job
- ✅ ZIP contains all expected files

### File List
**Files Modified:**
- [x] `backend/src/moodlelogsmart/main.py` (download_results function)

**Files Created:**
- None (implementation was already in main.py)

**Files to Delete:**
- None

### Change Log
- Story 2.3 implemented as part of initial API development
- Download endpoint functional since commit 8238ca1
- ZIP creation integrated with process_job background task
- Tests added in test_api.py

---

## 📚 References

**Epic 2**: docs/epics/EPIC-02-API-Layer.md
**Story 2.1**: Upload Endpoint (prerequisite)
**Story 2.2**: Status Endpoint (prerequisite)
**Story 2.4**: Job Management (prerequisite)
**FastAPI Docs**: https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse

---

## ✨ Notes for Developer

- FileResponse streams file efficiently (doesn't load into memory)
- ZIP created during processing, not on download
- Output files stored in TEMP_DIR with job_id prefix
- Consider cleanup strategy for old files (Story 2.4)
- Download doesn't delete file (allows multiple downloads)

---

**Created**: 2026-01-29
**Status**: ✅ Ready for Review
**Completed**: 2026-01-29 (retroactive documentation)
