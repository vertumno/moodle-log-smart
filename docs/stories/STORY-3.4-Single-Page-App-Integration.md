# Story 3.4: Single Page App Integration

**Story ID**: STORY-3.4
**Epic**: EPIC-03 (Frontend Minimalista)
**Status**: Draft
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 3
**Assigned to**: @dev (Dex)
**Estimate**: 1 dia

---

## 📖 User Story

**As a** usuário
**I want** interface fluida sem recarregar página
**So that** experiência seja moderna

---

## ✅ Acceptance Criteria

- [ ] Todos componentes em 1 arquivo (App.jsx) ou bem organizados
- [ ] Estados bem definidos: "upload", "processing", "completed", "error"
- [ ] Transição suave entre estados (sem jump ou flicker)
- [ ] Error handling com mensagem clara
- [ ] Styling minimalista com Tailwind CSS aplicado
- [ ] Layout responsivo (funciona em tablet/mobile)
- [ ] Title e descrição da aplicação visíveis
- [ ] App.jsx é o entry point principal

---

## 🎯 Context & Requirements

### Dependencies
- **Story 3.1**: UploadZone component completo
- **Story 3.2**: ProgressBar component completo
- **Story 3.3**: DownloadButton component completo
- **Frontend Setup**: React + Vite + Tailwind CSS

### Technical Details

**State Machine**:
```
Initial: "idle"
         ↓
User uploads → "upload" (UploadZone visible)
         ↓
File sent to API → "processing" (ProgressBar visible)
         ↓
Polling completes → "completed" (DownloadButton visible)
         ↓
Download clicked → "idle" (reset)

On error at any stage → "error" (error message visible)
```

**State Structure**:
```javascript
const [appState, setAppState] = useState("idle");
const [jobId, setJobId] = useState(null);
const [error, setError] = useState(null);
```

**Color Palette** (Tailwind):
- Primary: `blue-500` (#3B82F6)
- Success: `green-500` (#10B981)
- Error: `red-500` (#EF4444)
- Background: `gray-50` (#F9FAFB)
- Text: `gray-900` (#111827)

**Typography**:
- Title: "MoodleLogSmart 🧠"
- Subtitle: "Transforme seus logs do Moodle em análises pedagógicas"
- Footer: "✨ Zero configuração necessária!"

**Responsive Design**:
- Mobile: 1 column, padding, touch-friendly
- Tablet: 1 column with max-width
- Desktop: centered container

---

## 📋 Implementation Tasks

### Task 1: Create App.jsx (Main Component)
**Subtasks:**
- [ ] Create file: `frontend/src/App.jsx`
- [ ] Import React and useState
- [ ] Setup initial state (appState, jobId, error)
- [ ] Render basic layout structure

### Task 2: Implement State Machine
**Subtasks:**
- [ ] Define state transitions
- [ ] Create handlers:
  - `handleUploadSuccess(jobId)` → setState("processing")
  - `handleUploadError(error)` → setState("error")
  - `handleProcessingComplete(jobId)` → setState("completed")
  - `handleProcessingError(error)` → setState("error")
  - `handleDownloadComplete()` → setState("idle")
- [ ] Verify state transitions work

### Task 3: Conditionally Render Components
**Subtasks:**
- [ ] If appState === "idle" or "upload": Show UploadZone
- [ ] If appState === "processing": Show ProgressBar
- [ ] If appState === "completed": Show DownloadButton
- [ ] If appState === "error": Show error message
- [ ] Always show title and footer

### Task 4: Add Tailwind CSS Styling
**Subtasks:**
- [ ] Create `frontend/src/index.css` with Tailwind imports
- [ ] Setup color palette in Tailwind config (if needed)
- [ ] Apply classes to App.jsx structure:
  - Container: `min-h-screen flex flex-col items-center justify-center bg-gray-50`
  - Card: `bg-white rounded-lg shadow-lg p-8 max-w-md w-full`
  - Title: `text-3xl font-bold text-gray-900 text-center`
  - Components: padding, spacing, responsive

### Task 5: Implement Error Handling
**Subtasks:**
- [ ] Catch upload errors
- [ ] Catch processing errors
- [ ] Catch download errors
- [ ] Show error message with details
- [ ] Provide "Retry" button to reset state
- [ ] Don't show raw error messages to user

### Task 6: Add Responsive Design
**Subtasks:**
- [ ] Test on mobile (320px)
- [ ] Test on tablet (768px)
- [ ] Test on desktop (1200px)
- [ ] Adjust padding/margins for mobile
- [ ] Verify text is readable
- [ ] Verify buttons are touch-friendly

### Task 7: Create Supporting Files
**Subtasks:**
- [ ] Create `frontend/src/main.jsx` (Vite entry point)
- [ ] Create `frontend/index.html` (HTML template)
- [ ] Create `frontend/vite.config.js` (Vite config)
- [ ] Create `frontend/tailwind.config.js` (Tailwind config)
- [ ] Create `frontend/postcss.config.js` (PostCSS config)

### Task 8: Integration Testing
**Subtasks:**
- [ ] Test full flow: upload → processing → download
- [ ] Test error states at each step
- [ ] Test responsiveness on different screen sizes
- [ ] Test in Chrome, Firefox, Edge
- [ ] Verify no console errors

---

## 🎨 Component Structure

### App.jsx Layout
```jsx
<div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
  {/* Header */}
  <div className="text-center mb-8">
    <h1 className="text-4xl font-bold text-gray-900">MoodleLogSmart 🧠</h1>
    <p className="text-gray-600 mt-2">Transforme seus logs do Moodle</p>
    <p className="text-gray-500">em análises pedagógicas</p>
  </div>

  {/* Main Card */}
  <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
    {appState === "idle" || appState === "upload" && (
      <UploadZone onUploadSuccess={handleUploadSuccess} onUploadError={handleUploadError} />
    )}

    {appState === "processing" && (
      <ProgressBar jobId={jobId} onComplete={handleProcessingComplete} onError={handleProcessingError} />
    )}

    {appState === "completed" && (
      <DownloadButton jobId={jobId} disabled={false} onDownloadComplete={handleDownloadComplete} />
    )}

    {appState === "error" && (
      <div className="text-center">
        <p className="text-red-500 font-semibold mb-4">{error}</p>
        <button onClick={resetState} className="bg-blue-500 text-white px-6 py-2 rounded">
          Tentar Novamente
        </button>
      </div>
    )}
  </div>

  {/* Footer */}
  <footer className="text-center mt-8 text-gray-500">
    <p>✨ Zero configuração necessária!</p>
    <p className="text-sm mt-2">Resultados: CSV enriquecido + XES + Bloom</p>
  </footer>
</div>
```

---

## 🧪 Testing Strategy

**Integration Tests** (Full app flow):

1. **Test: Upload → Processing → Download Flow**
   - Render App
   - Upload CSV
   - Verify UploadZone hidden, ProgressBar shown
   - Wait for polling completion
   - Verify ProgressBar hidden, DownloadButton shown
   - Click download
   - Verify download triggered

2. **Test: Error at Upload Stage**
   - Render App
   - Try upload with invalid file
   - Verify error message shown
   - Click "Tentar Novamente"
   - Verify reset to upload state

3. **Test: Error at Processing Stage**
   - Mock API to fail at processing
   - Upload file
   - Wait for error
   - Verify error message shown
   - Verify "Tentar Novamente" button

4. **Test: Responsive Layout**
   - Render at mobile width (320px)
   - Verify layout doesn't break
   - Verify text readable
   - Verify buttons clickable
   - Render at tablet width (768px)
   - Render at desktop width (1200px)

5. **Test: No State Leaks**
   - Complete full flow
   - Click "Tentar Novamente"
   - Verify app resets completely
   - Verify no old jobId lingering

---

## 🔗 Dependencies & File Structure

### File Organization
```
frontend/
├── src/
│   ├── App.jsx                    # Main component (this story)
│   ├── main.jsx                   # Vite entry point
│   ├── index.css                  # Tailwind imports
│   ├── api.js                     # Optional: shared API client
│   └── components/
│       ├── UploadZone.jsx         # Story 3.1
│       ├── ProgressBar.jsx        # Story 3.2
│       └── DownloadButton.jsx     # Story 3.3
├── index.html                      # HTML template
├── package.json                    # Dependencies
├── vite.config.js                  # Vite config
├── tailwind.config.js              # Tailwind config
├── postcss.config.js               # PostCSS config
└── .gitignore
```

### Dependencies Required
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-dropzone": "^14.0.0"
  },
  "devDependencies": {
    "vite": "^4.0.0",
    "@vitejs/plugin-react": "^3.0.0",
    "tailwindcss": "^3.0.0",
    "postcss": "^8.0.0",
    "autoprefixer": "^10.0.0"
  }
}
```

---

## 📝 Dev Agent Record

### Checklist
- [ ] Task 1: App.jsx created with basic structure
- [ ] Task 2: State machine implemented
- [ ] Task 3: Conditional rendering working
- [ ] Task 4: Tailwind CSS applied
- [ ] Task 5: Error handling implemented
- [ ] Task 6: Responsive design verified
- [ ] Task 7: Supporting files created
- [ ] Task 8: Integration tests passing

### Debug Log
[Will be updated during development]

### Completion Notes
[Will be updated upon completion]

### File List
**Files to Create:**
- [ ] `frontend/src/App.jsx`
- [ ] `frontend/src/main.jsx`
- [ ] `frontend/src/index.css`
- [ ] `frontend/index.html`
- [ ] `frontend/vite.config.js`
- [ ] `frontend/tailwind.config.js`
- [ ] `frontend/postcss.config.js`
- [ ] `frontend/package.json` (updated)

**Files to Modify:**
- [ ] (None - this is new setup)

**Files to Delete:**
- [ ] (None)

### Change Log
- Created Story 3.4 from Epic 3 specification
- [Will add commits during development]

---

## 📚 References

**Epic 3**: docs/epics/EPIC-03-Frontend-Minimalista.md
**Story 3.1**: docs/stories/STORY-3.1-UploadZone-Component.md
**Story 3.2**: docs/stories/STORY-3.2-ProgressBar-Component.md
**Story 3.3**: docs/stories/STORY-3.3-DownloadButton-Component.md
**Tailwind Docs**: https://tailwindcss.com/
**Vite Docs**: https://vitejs.dev/
**React Docs**: https://react.dev/

---

## ✨ Notes for Developer

- This is the orchestration story - it brings all 3 components together
- Focus on state management: keep it simple and clear
- Responsive design is important for real users
- Error states should be friendly and recoverable
- Test the full flow end-to-end, not just individual states
- Keep styling minimal but clean - Tailwind makes this easy
- The app should feel fast and responsive

---

**Created**: 2026-01-29
**Status**: Draft → Ready for Dev → In Progress → Complete
