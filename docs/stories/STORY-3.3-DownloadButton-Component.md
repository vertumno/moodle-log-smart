# Story 3.3: DownloadButton Component

**Story ID**: STORY-3.3
**Epic**: EPIC-03 (Frontend Minimalista)
**Status**: Draft
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 3
**Assigned to**: @dev (Dex)
**Estimate**: 0.5 dia

---

## 📖 User Story

**As a** usuário
**I want** baixar ZIP com 1 clique
**So that** receba resultados rapidamente

---

## ✅ Acceptance Criteria

- [ ] Botão aparece apenas quando processamento completa (status === "completed")
- [ ] Clique baixa ZIP automaticamente
- [ ] Nome do arquivo: results_YYYYMMDD_HHMMSS.zip
- [ ] Botão tem ícone de download (⬇️ ou SVG)
- [ ] Show success feedback ("Download iniciado!")
- [ ] Handle download errors gracefully
- [ ] Button disabled durante download

---

## 🎯 Context & Requirements

### Dependencies
- **EPIC-02 (API Layer)**: Endpoint `GET /api/download/{job_id}` deve estar funcional
- **Story 3.2**: ProgressBar deve chamar onComplete quando completo
- **Frontend Setup**: React + Vite rodando

### Technical Details

**API Integration**:
- Call `GET /api/download/{jobId}`
- Response: Binary ZIP file (Content-Type: application/zip)
- Filename from header: Content-Disposition
- Fallback filename: `results_YYYYMMDD_HHMMSS.zip`

**Download Logic**:
- Fetch file as blob
- Create blob URL
- Create invisible <a> element
- Set href to blob URL
- Set download attribute with filename
- Trigger click()
- Cleanup blob URL

**UI States**:
- **Hidden**: When processing (status !== "completed")
- **Visible**: When processing complete
- **Downloading**: Show spinner, disable button
- **Complete**: Show success message, enable button again

**Styling**:
- Use Tailwind CSS
- Primary color: #3B82F6
- Success color: #10B981
- Icon: ⬇️ (emoji) or SVG download icon
- Button style: rounded, padding, hover effect

---

## 📋 Implementation Tasks

### Task 1: Create DownloadButton Component
**Subtasks:**
- [ ] Create file: `frontend/src/components/DownloadButton.jsx`
- [ ] Accept props: jobId, disabled
- [ ] Set state: { isDownloading: false, message: "" }
- [ ] Render button HTML

### Task 2: Implement Download Logic
**Subtasks:**
- [ ] Create function: handleDownload(jobId)
- [ ] Fetch: `GET /api/download/{jobId}`
- [ ] Check response.ok
- [ ] Convert response to blob
- [ ] Extract filename from response headers (or fallback)
- [ ] Create blob URL

### Task 3: Trigger Browser Download
**Subtasks:**
- [ ] Create <a> element (document.createElement('a'))
- [ ] Set href to blob URL
- [ ] Set download attribute to filename
- [ ] Append to body
- [ ] Trigger click()
- [ ] Remove element from body
- [ ] Revoke blob URL (URL.revokeObjectURL)

### Task 4: Add Loading State
**Subtasks:**
- [ ] Show spinner during download
- [ ] Disable button while downloading
- [ ] Show "Baixando..." text
- [ ] Hide spinner when complete

### Task 5: Add Success Feedback
**Subtasks:**
- [ ] Show "Download iniciado!" message
- [ ] Auto-dismiss after 3 seconds
- [ ] Or show toast notification

### Task 6: Handle Download Errors
**Subtasks:**
- [ ] Catch network errors
- [ ] Catch blob conversion errors
- [ ] Show error message to user
- [ ] Allow retry

### Task 7: Visibility Control
**Subtasks:**
- [ ] Only show button when parent passes: isComplete === true
- [ ] Or check if jobId exists
- [ ] Hidden state: display: none or return null

### Task 8: Write Component Tests
**Subtasks:**
- [ ] Mock fetch API
- [ ] Test: Button not visible when disabled
- [ ] Test: Click triggers download
- [ ] Test: Loading state shown
- [ ] Test: Success message shown
- [ ] Test: Error handling works
- [ ] Use Jest + React Testing Library

---

## 🎨 Component Interface

### Props
```javascript
DownloadButton.propTypes = {
  jobId: PropTypes.string.isRequired,          // UUID from upload
  disabled: PropTypes.bool,                    // Hide button
  onDownloadStart: PropTypes.func,             // () => void
  onDownloadComplete: PropTypes.func,          // () => void
  onDownloadError: PropTypes.func,             // (error) => void
}
```

### Behavior
```javascript
// When user clicks button:
1. Show loading spinner
2. Disable button
3. Fetch GET /api/download/{jobId}
4. Convert to blob
5. Trigger browser download
6. Show success message
7. Hide spinner after 2 seconds
8. Re-enable button

// If error:
1. Show error message
2. Allow retry
3. Re-enable button
```

### HTML Structure
```
<button className="download-button">
  <span className="icon">⬇️</span>
  <span className="text">Baixar Resultados (ZIP)</span>
  {isDownloading && <span className="spinner">⏳</span>}
</button>

{message && <p className="message">{message}</p>}
```

---

## 🧪 Testing Strategy

**Unit Tests** (Jest + React Testing Library):

1. **Test: Button Visibility**
   - Render with disabled={true}
   - Verify button not visible
   - Render with disabled={false}
   - Verify button visible

2. **Test: Download Trigger**
   - Mock fetch to return blob
   - Click button
   - Verify fetch called with correct jobId

3. **Test: Loading State**
   - Click button
   - Verify spinner shows
   - Verify button disabled
   - Wait for fetch
   - Verify spinner hidden

4. **Test: Success Message**
   - Download completes
   - Verify "Download iniciado!" shown
   - Wait 3 seconds
   - Verify message disappears

5. **Test: Error Handling**
   - Mock fetch to throw error
   - Click button
   - Verify error message shown
   - Verify button re-enabled

6. **Test: Blob URL Cleanup**
   - Mock URL.revokeObjectURL
   - Download completes
   - Verify revokeObjectURL called

---

## 🔗 Dependencies & Integration

### External Dependencies
- React hooks (useState, useCallback)
- Fetch API (built-in)
- Blob API (built-in)
- URL.createObjectURL / URL.revokeObjectURL (built-in)

### API Integration
- **Endpoint**: `GET /api/download/{jobId}`
- **Response**: Binary ZIP file
- **Content-Type**: application/zip
- **Filename**: From Content-Disposition header or fallback

### Component Consumption
- Parent: `App.jsx` (controls visibility based on status)
- Shown after: ProgressBar completes successfully

---

## 🐛 Error Handling

| Error | Handling |
|-------|----------|
| Job not found (404) | Show "Job not found" |
| Download fails | Show "Download failed, try again" |
| Network error | Show "Network error during download" |
| Blob conversion fails | Show "Error processing file" |

---

## 📝 Dev Agent Record

### Checklist
- [ ] Task 1: DownloadButton.jsx created
- [ ] Task 2: Download logic implemented
- [ ] Task 3: Browser download triggered
- [ ] Task 4: Loading state working
- [ ] Task 5: Success feedback displayed
- [ ] Task 6: Error handling working
- [ ] Task 7: Visibility controlled by parent
- [ ] Task 8: All tests passing

### Debug Log
[Will be updated during development]

### Completion Notes
[Will be updated upon completion]

### File List
**Files to Create:**
- [ ] `frontend/src/components/DownloadButton.jsx`
- [ ] `frontend/src/components/DownloadButton.test.jsx`

**Files to Modify:**
- [ ] `frontend/src/App.jsx` (import and use DownloadButton)

**Files to Delete:**
- [ ] (None)

### Change Log
- Created Story 3.3 from Epic 3 specification
- [Will add commits during development]

---

## 📚 References

**Epic 3**: docs/epics/EPIC-03-Frontend-Minimalista.md
**API Documentation**: backend/API.md (GET /api/download/{job_id})
**Story 3.2**: docs/stories/STORY-3.2-ProgressBar-Component.md

---

## ✨ Notes for Developer

- This is a small story (0.5 days) - should be quick
- Focus on smooth UX: loading state, success feedback
- Browser download handling is straightforward
- Key: proper cleanup of blob URLs to avoid memory leaks
- Test error cases thoroughly - downloads can fail in many ways
- Keep button focused: just download, nothing else

---

**Created**: 2026-01-29
**Status**: Draft → Ready for Dev → In Progress → Complete
