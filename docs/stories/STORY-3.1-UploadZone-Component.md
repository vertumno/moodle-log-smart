# Story 3.1: UploadZone Component

**Story ID**: STORY-3.1
**Epic**: EPIC-03 (Frontend Minimalista)
**Status**: Draft
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 3
**Assigned to**: @dev (Dex)
**Estimate**: 1 dia

---

## 📖 User Story

**As a** usuário
**I want** arrastar CSV para zona de upload
**So that** envio seja rápido e intuitivo

---

## ✅ Acceptance Criteria

- [ ] Zona de upload visível e destacada na página
- [ ] Drag & drop funciona (usuário arrasta arquivo sobre zona)
- [ ] Click to browse funciona (botão para selecionar arquivo)
- [ ] Valida arquivo é .csv (rejeita outros tipos com mensagem de erro)
- [ ] Mostra nome do arquivo após seleção
- [ ] Loading spinner durante upload
- [ ] Success message após upload bem-sucedido
- [ ] Error message se upload falhar

---

## 🎯 Context & Requirements

### Dependencies
- **EPIC-02 (API Layer)**: Endpoint `POST /api/upload` deve estar funcional
- **Frontend Setup**: React + Vite deve estar rodando
- **Library**: react-dropzone para drag & drop

### Technical Details

**Integration with API**:
- Call `POST /api/upload` with multipart/form-data
- Send file in field named "file"
- Receive response: `{ job_id, status, message }`
- Return job_id to parent component for polling

**Validation (Client-side)**:
- File extension: .csv only
- Show error: "Only .csv files are allowed"
- Prevent upload if validation fails

**UI States**:
- **Idle**: Zone visible, ready for input
- **Dragging**: Visual feedback (border highlight, background change)
- **Uploading**: Show spinner, disable interactions
- **Success**: Show job_id received, enable next step
- **Error**: Show error message, allow retry

**Styling**:
- Use Tailwind CSS
- Colors from Epic 3 palette (Primary: #3B82F6)
- Border: dashed, rounded corners
- Icon: 📁 (file emoji or SVG)

---

## 📋 Implementation Tasks

### Task 1: Setup React App (Vite)
**Subtasks:**
- [ ] Verify Vite is running (`npm run dev`)
- [ ] Verify frontend/ directory structure exists
- [ ] Verify package.json has React and Vite dependencies

### Task 2: Install react-dropzone
**Subtasks:**
- [ ] Run: `npm install react-dropzone`
- [ ] Verify import works: `import { useDropzone } from 'react-dropzone'`

### Task 3: Create UploadZone Component
**Subtasks:**
- [ ] Create file: `frontend/src/components/UploadZone.jsx`
- [ ] Import useDropzone hook
- [ ] Implement onDrop callback
- [ ] Implement getRootProps and getInputProps
- [ ] Render upload zone HTML (div, input, icon, text)
- [ ] Add Tailwind styling

### Task 4: Implement File Validation (Client-side)
**Subtasks:**
- [ ] Check file.type or file.name extension
- [ ] Show error message if not .csv
- [ ] Prevent upload if validation fails
- [ ] Log validation errors

### Task 5: Call API Upload Endpoint
**Subtasks:**
- [ ] Create function: uploadFile(file) in component
- [ ] Call: `fetch('/api/upload', { method: 'POST', body: FormData })`
- [ ] Handle response: extract job_id
- [ ] Pass job_id to parent via callback prop
- [ ] Log API errors

### Task 6: Add Loading Spinner
**Subtasks:**
- [ ] Add state: isLoading (boolean)
- [ ] Show spinner during upload (isLoading === true)
- [ ] Hide spinner when complete
- [ ] Disable zone while loading

### Task 7: Display Success/Error Messages
**Subtasks:**
- [ ] Show success message when upload completes
- [ ] Show error message if upload fails
- [ ] Auto-dismiss success message after 2 seconds
- [ ] Allow retry on error

### Task 8: Write Component Tests
**Subtasks:**
- [ ] Test: File drop triggers upload
- [ ] Test: Click to browse works
- [ ] Test: CSV files accepted, others rejected
- [ ] Test: Loading state displays correctly
- [ ] Use Jest + React Testing Library

---

## 🎨 Component Interface

### Props
```javascript
UploadZone.propTypes = {
  onUploadSuccess: PropTypes.func.isRequired,  // (jobId) => void
  onUploadError: PropTypes.func,               // (error) => void
  disabled: PropTypes.bool,                    // Disable during processing
}
```

### Returns
```javascript
// Calls onUploadSuccess with:
{ jobId: "uuid-string" }

// Calls onUploadError with:
{ message: "error message" }
```

### HTML Structure
```
<div className="upload-zone">
  <input (hidden)>
  <div className="zone-content">
    <icon>📁</icon>
    <h2>Arraste seu CSV aqui ou clique</h2>
    <p>Suporta logs exportados do Moodle</p>
  </div>
</div>
```

---

## 🧪 Testing Strategy

**Unit Tests** (Jest + React Testing Library):

1. **Test: Drag & Drop**
   - Simulate drag over zone
   - Verify visual feedback (className change)
   - Drop .csv file
   - Verify upload called

2. **Test: Click to Browse**
   - Click on zone
   - Verify file input dialog opens
   - Select .csv file
   - Verify upload called

3. **Test: File Validation**
   - Try to upload .txt file
   - Verify error message shown
   - Verify API not called

4. **Test: Loading State**
   - Upload file
   - Verify spinner shown
   - Wait for response
   - Verify spinner hidden

5. **Test: Success Feedback**
   - Upload succeeds
   - Verify onUploadSuccess called with jobId
   - Verify success message shown

6. **Test: Error Feedback**
   - Upload fails
   - Verify onUploadError called
   - Verify error message shown

---

## 🔗 Dependencies & Integration

### External Dependencies
- `react-dropzone` (npm package)
- React hooks (useState, useCallback)
- Fetch API (built-in)

### API Integration
- **Endpoint**: `POST /api/upload`
- **Content-Type**: multipart/form-data
- **Response**: `{ job_id, status, message }`

### Component Consumption
- Parent: `App.jsx` (calls UploadZone, receives job_id)
- Next Component: `ProgressBar` (receives job_id from parent)

---

## 🐛 Error Handling

| Error | Handling |
|-------|----------|
| File not .csv | Show error message, allow retry |
| Upload fails (network) | Show error message with retry button |
| API returns error | Show error from response.detail |
| File too large (>50MB) | Show size error from API |

---

## 📝 Dev Agent Record

### Checklist
- [ ] Task 1: Setup verified
- [ ] Task 2: react-dropzone installed
- [ ] Task 3: UploadZone.jsx created and styled
- [ ] Task 4: File validation working
- [ ] Task 5: API integration complete
- [ ] Task 6: Loading spinner working
- [ ] Task 7: Success/error messages displaying
- [ ] Task 8: All tests passing

### Debug Log
[Will be updated during development]

### Completion Notes
[Will be updated upon completion]

### File List
**Files to Create:**
- [ ] `frontend/src/components/UploadZone.jsx`
- [ ] `frontend/src/components/UploadZone.test.jsx`

**Files to Modify:**
- [ ] `frontend/src/App.jsx` (import and use UploadZone)

**Files to Delete:**
- [ ] (None)

### Change Log
- Created Story 3.1 from Epic 3 specification
- [Will add commits during development]

---

## 📚 References

**Epic 3**: docs/epics/EPIC-03-Frontend-Minimalista.md
**API Documentation**: backend/API.md (POST /api/upload)
**Tailwind Colors**: #3B82F6 (primary), #10B981 (success), #EF4444 (error)

---

## ✨ Notes for Developer

- Keep component simple and focused
- No routing needed (single page app)
- Parent component will handle state management
- Focus on UX: make drag & drop intuitive
- Use Tailwind for consistent styling
- Test on Chrome/Firefox/Edge

---

**Created**: 2026-01-29
**Status**: Draft → Ready for Dev → In Progress → Complete
