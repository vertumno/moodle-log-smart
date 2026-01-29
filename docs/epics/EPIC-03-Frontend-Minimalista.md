# Epic 3: Frontend Minimalista (1 Página)

**Epic ID**: EPIC-03
**Product**: MoodleLogSmart
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 3
**Duration**: 3-4 dias
**Status**: Not Started
**Epic Owner**: @dev
**Dependencies**: EPIC-02 (API Layer)

---

## 📋 Epic Overview

### Epic Goal
Criar **interface web de 1 página única** com UX de 3 cliques: Upload → Processar → Download.

### Business Value
- **Zero fricção**: Usuário não precisa navegar entre páginas
- **Experiência moderna**: Drag & drop, progress bar, download instantâneo
- **Acessibilidade**: Interface simples para usuários não-técnicos

### Success Criteria
- ✅ Interface funciona em 1 página (sem routing)
- ✅ Usuário completa fluxo em <3 cliques
- ✅ Progress bar atualiza em tempo real
- ✅ Download ZIP funciona em Chrome, Firefox, Edge
- ✅ Interface é responsiva (funciona em tablet)

---

## 👥 User Stories

### Story 3.1: UploadZone Component
**As a** usuário
**I want** arrastar CSV para zona de upload
**So that** envio seja rápido e intuitivo

**Acceptance Criteria**:
- ✅ Zona de upload visível e destacada
- ✅ Drag & drop funciona
- ✅ Click to browse funciona
- ✅ Valida arquivo é .csv (mostra erro se não)
- ✅ Mostra nome do arquivo após upload
- ✅ Loading state durante upload

**Tasks**:
- [ ] Setup React app (Vite)
- [ ] Instalar react-dropzone
- [ ] Criar UploadZone component
- [ ] Validação de arquivo (client-side)
- [ ] Upload para `/api/upload`
- [ ] Loading spinner

**Estimate**: 1 dia

---

### Story 3.2: ProgressBar Component
**As a** usuário
**I want** ver progresso em tempo real
**So that** saiba quanto tempo falta

**Acceptance Criteria**:
- ✅ Progress bar mostra % (0-100)
- ✅ Atualiza a cada 5 segundos (polling)
- ✅ Mostra mensagem de status ("Enriching activities...")
- ✅ Mostra sucesso quando completo
- ✅ Mostra erro se falhar

**Tasks**:
- [ ] Criar ProgressBar component
- [ ] Implementar polling (setInterval)
- [ ] Fetch `/api/status/{job_id}` a cada 5s
- [ ] Atualizar UI com resposta
- [ ] Stop polling quando completo/failed

**Estimate**: 1 dia

---

### Story 3.3: DownloadButton Component
**As a** usuário
**I want** baixar ZIP com 1 clique
**So that** receba resultados rapidamente

**Acceptance Criteria**:
- ✅ Botão aparece quando processamento completa
- ✅ Clique baixa ZIP automaticamente
- ✅ Nome do arquivo: results_YYYYMMDD_HHMMSS.zip
- ✅ Botão tem ícone de download

**Tasks**:
- [ ] Criar DownloadButton component
- [ ] Fetch `/api/download/{job_id}`
- [ ] Trigger browser download
- [ ] Success feedback (toast/alert)

**Estimate**: 0.5 dia

---

### Story 3.4: Single Page App Integration
**As a** usuário
**I want** interface fluida sem recarregar página
**So that** experiência seja moderna

**Acceptance Criteria**:
- ✅ Todos componentes em 1 arquivo (App.jsx)
- ✅ Estados: "upload", "processing", "completed"
- ✅ Transição suave entre estados
- ✅ Error handling (mostra mensagem clara)
- ✅ Styling minimalista (Tailwind CSS)

**Tasks**:
- [ ] Criar App.jsx (estado global)
- [ ] State machine (upload → processing → completed)
- [ ] Integrar componentes
- [ ] Adicionar Tailwind CSS
- [ ] Error boundaries

**Estimate**: 1 dia

---

## 🎨 UI/UX Design

### Layout

```
┌──────────────────────────────────────────────────┐
│              MoodleLogSmart 🧠                   │
│     Transforme seus logs do Moodle              │
│        em análises pedagógicas                   │
│                                                  │
│  ╔════════════════════════════════════════════╗ │
│  ║                                            ║ │
│  ║    📁  Arraste seu CSV aqui ou clique     ║ │
│  ║                                            ║ │
│  ║      Suporta logs exportados do Moodle     ║ │
│  ║                                            ║ │
│  ╚════════════════════════════════════════════╝ │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │  Processando... ████████░░░░  67%       │  │
│  │  Enriquecendo atividades...              │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│         [ ⬇️  Baixar Resultados (ZIP) ]        │
│                                                  │
│  Resultados: CSV enriquecido + XES + Bloom     │
│  ✨ Zero configuração necessária!              │
└──────────────────────────────────────────────────┘
```

### Color Palette (Minimalista)
- **Primary**: #3B82F6 (blue-500)
- **Success**: #10B981 (green-500)
- **Error**: #EF4444 (red-500)
- **Background**: #F9FAFB (gray-50)
- **Text**: #111827 (gray-900)

---

## 📁 File Structure

```
frontend/
├── src/
│   ├── App.jsx                 # Single page app
│   ├── api.js                  # API client (fetch)
│   ├── main.jsx                # Entry point
│   └── index.css               # Tailwind CSS
├── package.json
├── vite.config.js
└── index.html
```

---

## 🧪 Testing Strategy

### Component Tests
- **UploadZone**: 4 test cases
  - Drag & drop
  - Click to browse
  - File validation
  - Upload success

- **ProgressBar**: 3 test cases
  - Progress updates
  - Polling mechanism
  - Completion state

- **DownloadButton**: 2 test cases
  - Download trigger
  - File download

### E2E Test
- **Full flow**: Upload → Wait → Download
  - Use Playwright/Cypress
  - Simulate real user interaction

---

## ✅ Definition of Done

- ✅ Interface de 1 página funcional
- ✅ Usuário completa fluxo em <3 cliques
- ✅ Progress bar atualiza corretamente
- ✅ Download funciona em Chrome/Firefox/Edge
- ✅ Responsivo (tablet)
- ✅ Styling aplicado (Tailwind)
- ✅ E2E test passa

---

**Epic Owner**: @dev
**Reviewer**: @ux-design-expert
**Approver**: @pm (Morgan)