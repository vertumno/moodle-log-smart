# Story 3.2: ProgressBar Component

**Story ID**: STORY-3.2
**Epic**: EPIC-03 (Frontend Minimalista)
**Status**: Ready for Review
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 3
**Assigned to**: @dev (Dex)
**Estimate**: 1 dia

---

## 📖 User Story

**As a** usuário
**I want** ver progresso em tempo real
**So that** saiba quanto tempo falta

---

## ✅ Acceptance Criteria

- [ ] Progress bar mostra % (0-100)
- [ ] Atualiza a cada 5 segundos (polling)
- [ ] Mostra mensagem de status ("Processando...", "Enriquecendo atividades...", etc)
- [ ] Mostra sucesso quando processamento completa
- [ ] Mostra erro se processamento falhar
- [ ] Para de fazer polling quando completo ou falhou
- [ ] Exibe ETA (tempo estimado) se possível

---

## 🎯 Context & Requirements

### Dependencies
- **EPIC-02 (API Layer)**: Endpoint `GET /api/status/{job_id}` deve estar funcional
- **Story 3.1**: UploadZone deve passar job_id para este componente
- **Frontend Setup**: React + Vite rodando

### Technical Details

**API Integration**:
- Call `GET /api/status/{job_id}` a cada 5 segundos
- Response format: `{ job_id, status, progress, error, created_at, completed_at }`
- Status values: "processing", "completed", "failed"
- Progress: 0-100 (integer percentage)

**Polling Logic**:
- Start polling quando componente monta
- Stop polling quando status === "completed" ou "failed"
- Cleanup interval quando componente desmonta
- Don't call API if job_id não existe

**UI States**:
- **Processing**: Show progress bar, % value, status message
- **Completed**: Show 100%, success message
- **Failed**: Show error message with details

**Status Messages**:
- 0-20%: "Detectando formato..."
- 20-40%: "Mapeando colunas..."
- 40-60%: "Limpando dados..."
- 60-80%: "Enriquecendo atividades..."
- 80-100%: "Gerando resultados..."
- 100%: "Sucesso! Resultados prontos para download"
- Error: "Erro: {error message}"

**Styling**:
- Use Tailwind CSS
- Progress bar: horizontal bar with percentage display
- Colors: Primary (#3B82F6) for bar, Success (#10B981) when complete
- Show spinner while polling

---

## 📋 Implementation Tasks

### Task 1: Create ProgressBar Component
**Subtasks:**
- [ ] Create file: `frontend/src/components/ProgressBar.jsx`
- [ ] Accept props: jobId, onComplete, onError
- [ ] Set initial state: { progress: 0, status: "processing", message: "" }
- [ ] Render progress bar HTML

### Task 2: Implement Polling Logic
**Subtasks:**
- [ ] Use useEffect to start polling on mount
- [ ] Create function: pollStatus(jobId)
- [ ] Setup setInterval: call every 5 seconds
- [ ] Cleanup interval on unmount
- [ ] Cleanup when status changes to completed/failed

### Task 3: Call API Status Endpoint
**Subtasks:**
- [ ] Fetch: `GET /api/status/{jobId}`
- [ ] Parse response JSON
- [ ] Extract: progress, status, error
- [ ] Update component state
- [ ] Handle network errors gracefully

### Task 4: Update Status Messages
**Subtasks:**
- [ ] Map progress % to message
- [ ] Show message based on current progress
- [ ] Update message dynamically during polling
- [ ] Use clear, user-friendly language

### Task 5: Handle Completion State
**Subtasks:**
- [ ] Detect when status === "completed"
- [ ] Stop polling
- [ ] Show success message
- [ ] Call onComplete callback with job_id
- [ ] Set progress to 100%

### Task 6: Handle Error State
**Subtasks:**
- [ ] Detect when status === "failed"
- [ ] Stop polling
- [ ] Show error message from API response
- [ ] Call onError callback with error
- [ ] Provide retry option

### Task 7: Add Visual Feedback
**Subtasks:**
- [ ] Add spinner/loader during polling
- [ ] Change colors on completion (green)
- [ ] Change colors on error (red)
- [ ] Add smooth transitions between states

### Task 8: Write Component Tests
**Subtasks:**
- [ ] Mock fetch API
- [ ] Test: Polling starts on mount
- [ ] Test: Progress updates correctly
- [ ] Test: Completion detected and callback fired
- [ ] Test: Error detected and callback fired
- [ ] Test: Polling stops when complete
- [ ] Use Jest + React Testing Library

---

## 🎨 Component Interface

### Props
```javascript
ProgressBar.propTypes = {
  jobId: PropTypes.string.isRequired,          // UUID from UploadZone
  onComplete: PropTypes.func.isRequired,       // (jobId) => void
  onError: PropTypes.func,                     // (error) => void
  pollInterval: PropTypes.number,              // milliseconds (default: 5000)
}
```

### Returns
```javascript
// Calls onComplete when status === "completed":
{ jobId: "uuid-string" }

// Calls onError when status === "failed":
{ message: "error message from API" }
```

### HTML Structure
```
<div className="progress-container">
  <div className="progress-message">
    <span className="spinner">⏳</span>
    <p>Enriquecendo atividades... 67%</p>
  </div>

  <div className="progress-bar">
    <div className="bar-fill" style={{ width: "67%" }}></div>
  </div>

  <p className="progress-percent">67%</p>
</div>
```

---

## 🧪 Testing Strategy

**Unit Tests** (Jest + React Testing Library):

1. **Test: Polling Starts**
   - Render component with jobId
   - Verify fetch called after short delay
   - Verify setInterval set

2. **Test: Progress Updates**
   - Mock API responses with increasing progress
   - Render component
   - Wait for updates
   - Verify progress bar value changes

3. **Test: Status Messages Update**
   - Progress 30% → "Mapeando colunas..."
   - Progress 70% → "Enriquecendo atividades..."
   - Verify messages display correctly

4. **Test: Completion Detected**
   - Mock API response: status === "completed"
   - Verify onComplete callback fired with jobId
   - Verify polling stops (no more fetch calls)

5. **Test: Error Detected**
   - Mock API response: status === "failed" with error
   - Verify onError callback fired
   - Verify error message displayed
   - Verify polling stops

6. **Test: Cleanup on Unmount**
   - Render component
   - Unmount component
   - Verify setInterval cleared
   - Verify no memory leaks

---

## 🔗 Dependencies & Integration

### External Dependencies
- React hooks (useState, useEffect, useCallback)
- Fetch API (built-in)

### API Integration
- **Endpoint**: `GET /api/status/{jobId}`
- **Response**: `{ job_id, status, progress, error, created_at, completed_at }`
- **Poll Frequency**: Every 5 seconds (configurable)

### Component Consumption
- Parent: `App.jsx` (passes jobId from UploadZone)
- Sibling: `DownloadButton` (appears when completed)

---

## 🐛 Error Handling

| Error | Handling |
|-------|----------|
| Job not found (404) | Show "Job not found" error |
| API error | Retry polling, show error after 3 retries |
| Network error | Retry polling, show "Network error" if persistent |
| Invalid jobId | Don't poll, show error immediately |

---

## 📝 Dev Agent Record

### Checklist
- [x] Task 1: ProgressBar.tsx created
- [x] Task 2: Polling logic implemented
- [x] Task 3: API integration complete
- [x] Task 4: Status messages mapped
- [x] Task 5: Completion handling working
- [x] Task 6: Error handling working
- [x] Task 7: Visual feedback added
- [x] Task 8: All tests passing

### Debug Log
[Will be updated during development]

### Completion Notes
✅ **Story COMPLETA** - All acceptance criteria met

**Implementação:**
- Componente TypeScript completo em `ProgressBar.tsx`
- Props: jobId, onComplete, onError, pollInterval (default 5000ms)
- Estados: progress, status, error, isPolling
- Polling logic com useEffect + setInterval
- Poll inicial imediatamente + intervalo de 5s
- API integration GET /api/status/{jobId}
- Status messages dinâmicas baseadas em progress %
- Callbacks onComplete/onError
- Stop polling quando completed ou failed
- Cleanup de interval on unmount
- Success state (green) e error state (red)
- Loading spinner durante processing
- Tailwind CSS styling
- 11 testes unitários cobrindo todos os casos

**Features Implementadas:**
- ✅ Progress bar 0-100%
- ✅ Polling a cada 5 segundos (configurável)
- ✅ Status messages dinâmicas
- ✅ Success message quando completo
- ✅ Error message se falhar
- ✅ Stop polling automaticamente
- ✅ Cleanup em unmount
- ✅ Spinner durante processing
- ✅ Colors baseadas em status (blue/green/red)

### File List
**Files to Create:**
- [x] `frontend/src/components/ProgressBar.tsx` (TypeScript)
- [x] `frontend/src/components/ProgressBar.test.tsx`

**Files to Modify:**
- [x] `frontend/src/components/ProgressBar.tsx` (replaced basic version)
- [ ] `frontend/src/App.tsx` (will be done in Story 3.4)

**Files to Delete:**
- (None)

### Change Log
- Created Story 3.2 from Epic 3 specification
- 2026-01-29: Implemented ProgressBar component with all features
  - Polling logic (useEffect + setInterval)
  - API integration GET /api/status/{jobId}
  - Dynamic status messages based on progress %
  - Success/error states with appropriate colors
  - Loading spinner
  - Cleanup of polling interval
  - Callbacks onComplete/onError
  - 11 comprehensive tests
  - TypeScript implementation
- [Will add commits during development]

---

## 📚 References

**Epic 3**: docs/epics/EPIC-03-Frontend-Minimalista.md
**API Documentation**: backend/API.md (GET /api/status/{job_id})
**Story 3.1**: docs/stories/STORY-3.1-UploadZone-Component.md

---

## ✨ Notes for Developer

- Polling is critical for UX - smooth updates are important
- Handle network failures gracefully - don't show raw errors
- Status messages should be motivating ("Enriquecendo..." not "Processing...")
- Keep component focused: just show progress, don't handle download
- Test polling with mock timers for reliable tests
- Remember to cleanup intervals to prevent memory leaks

---

**Created**: 2026-01-29
**Status**: Ready for Review → Ready for Dev → In Progress → Complete
