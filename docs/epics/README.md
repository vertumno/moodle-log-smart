# MoodleLogSmart - Epics Overview

Este diretório contém os **4 epics principais** que estruturam o desenvolvimento do MoodleLogSmart MVP.

---

## 📊 Epic Summary

| Epic ID | Nome | Sprint | Duração | Status | Owner |
|---------|------|--------|---------|--------|-------|
| **EPIC-01** | Backend Core + Auto-Detection | Sprint 1 | 1 semana (5 dias) | ✅ Completed | @dev |
| **EPIC-02** | API Layer Simplificada | Sprint 2 | 3-4 dias | ⏳ In Progress | @dev |
| **EPIC-03** | Frontend Minimalista | Sprint 3 | 3-4 dias | ⏳ In Progress | @dev |
| **EPIC-04** | Docker + Deployment | Sprint 4 | 2-3 dias | ⏳ Ready | @devops |

**Total Timeline**: **2-3 semanas** (14-18 dias úteis)

---

## 🎯 Epic Breakdown

### [EPIC-01: Backend Core + Auto-Detection](./EPIC-01-Backend-Core-AutoDetection.md)
**Goal**: Pipeline funcional (CSV → ZIP) com auto-detection inteligente

**Key Features**:
- ✨ Auto-detection de encoding, delimiter, colunas, timestamp
- 🧹 Data cleaning automático (filtros de role e eventos)
- 🏷️ Enriquecimento semântico com 13 regras Bloom
- 📦 Export multi-formato (CSV + XES + ZIP)

**User Stories**: 7 stories
- Story 1.1: Auto-Detection de Encoding e Delimiter
- Story 1.2: Auto-Mapeamento de Colunas Moodle
- Story 1.3: Auto-Detection de Formato de Timestamp
- Story 1.4: Data Cleaning com Configuração Default
- Story 1.5: Rule Engine + 13 Regras Bloom
- Story 1.6: Export Multi-Formato (CSV + XES)
- Story 1.7: ZIP Packager

**Deliverables**:
- Pipeline completo funcional
- Tests unitários >50% coverage
- Integration test end-to-end

---

### [EPIC-02: API Layer Simplificada](./EPIC-02-API-Layer.md)
**Goal**: API REST minimalista com 3 endpoints

**Key Features**:
- 📤 Upload de CSV (multipart/form-data)
- 📊 Status de processamento (polling)
- ⬇️ Download de ZIP de resultados

**User Stories**: 4 stories
- Story 2.1: Endpoint de Upload
- Story 2.2: Endpoint de Status
- Story 2.3: Endpoint de Download
- Story 2.4: Job Management & Error Handling

**Deliverables**:
- FastAPI app com 3 endpoints
- OpenAPI docs automáticas
- Tests de API >80% coverage

---

### [EPIC-03: Frontend Minimalista](./EPIC-03-Frontend-Minimalista.md)
**Goal**: Interface web de 1 página (3 cliques)

**Key Features**:
- 🎨 Upload zone com drag & drop
- 📈 Progress bar com polling
- ⬇️ Download button para ZIP
- ✨ Zero configuração manual

**User Stories**: 4 stories
- Story 3.1: UploadZone Component
- Story 3.2: ProgressBar Component
- Story 3.3: DownloadButton Component
- Story 3.4: Single Page App Integration

**Deliverables**:
- React app (1 página)
- Styling com Tailwind CSS
- E2E test

---

### [EPIC-04: Docker + Deployment](./EPIC-04-Docker-Deployment.md)
**Goal**: Deploy com 1 comando

**Key Features**:
- 🐳 Dockerfiles otimizados (backend + frontend)
- 🎼 docker-compose.yml
- 📖 README com quick start de 3 linhas
- ✅ Cross-platform (Windows, macOS, Linux)

**User Stories**: 4 stories
- Story 4.1: Dockerfile Backend
- Story 4.2: Dockerfile Frontend
- Story 4.3: Docker Compose
- Story 4.4: Documentation

**Deliverables**:
- Docker containers funcionais
- `docker-compose up` funciona
- Documentation completa

---

## 📈 Progress Tracking

### Overall Progress

```
┌─────────────────────────────────────────────────────────────┐
│  Sprint 1: Backend Core        [██████████] 7/7 stories     │
│  Sprint 2: API Layer           [████░░░░░░] 2/4 stories     │
│  Sprint 3: Frontend            [████░░░░░░] 2/4 stories     │
│  Sprint 4: Docker              [██░░░░░░░░] 1/4 stories     │
│  ───────────────────────────────────────────────────────    │
│  Total: 12/19 stories completed (63%)                       │
└─────────────────────────────────────────────────────────────┘
```

### Velocity Tracking
- **Sprint 1**: Target 7 stories / 5 days = 1.4 stories/day
- **Sprint 2**: Target 4 stories / 4 days = 1.0 stories/day
- **Sprint 3**: Target 4 stories / 4 days = 1.0 stories/day
- **Sprint 4**: Target 4 stories / 3 days = 1.3 stories/day

---

## 🎯 Critical Path

### Dependencies Flow
```
EPIC-01 (Backend)
   ↓
EPIC-02 (API) → Must complete EPIC-01 first
   ↓
EPIC-03 (Frontend) → Must complete EPIC-02 first
   ↓
EPIC-04 (Docker) → Must complete EPIC-01, EPIC-02, EPIC-03
```

### Parallel Work Opportunities
- **Documentation** pode começar em paralelo com EPIC-03
- **Testing** pode começar em paralelo com cada epic
- **Code review** acontece continuamente

---

## 🚀 Launch Checklist

### MVP Launch Requirements (All Epics Must Complete)

**Functional**:
- ✅ Backend pipeline processa CSV → ZIP
- ✅ API aceita upload, retorna status, serve download
- ✅ Frontend permite upload → visualizar progresso → download
- ✅ Docker compose inicia sistema completo

**Quality**:
- ✅ Tests unitários >50% coverage (backend)
- ✅ Tests de API >80% coverage
- ✅ E2E test passa (upload → download)
- ✅ Funciona em 3 OS (Windows, macOS, Linux)

**Documentation**:
- ✅ README com quick start
- ✅ API docs (OpenAPI)
- ✅ Architecture docs
- ✅ Troubleshooting guide

**Success Metrics**:
- ✅ Usuário completa fluxo em <3 cliques
- ✅ Processa 5000 eventos em <2 minutos
- ✅ Deploy com `docker-compose up` funciona first try

---

## 📝 Next Steps

### After Epic Creation
1. **Review with @architect** - Validar arquitetura técnica
2. **Stakeholder approval** - Obter sign-off de stakeholders
3. **Begin Sprint 1** - Iniciar desenvolvimento (EPIC-01)
4. **Daily stand-ups** - Track progress diariamente
5. **Sprint reviews** - Demo ao final de cada sprint

### Ongoing Activities
- **Code review**: Contínuo durante desenvolvimento
- **Testing**: Incremental (unitários + integração)
- **Documentation**: Atualizar à medida que implementa
- **Risk monitoring**: Track riscos e mitigações

---

## 🤝 Stakeholder Communication

### Weekly Updates
**Format**: Email summary
**Content**:
- Stories completed this week
- Blockers and risks
- Next week's focus
- Demo video/screenshots

### Sprint Reviews
**Frequency**: Ao final de cada sprint
**Attendees**: Product Manager, Stakeholders, Dev Team
**Format**: Live demo + Q&A

---

## 📚 Related Documents

- **PRD**: `../PRD-MoodleLogSmart.md`
- **Plan**: `../../.claude/plans/indexed-wibbling-sky.md`
- **Architecture**: (To be created by @architect)
- **API Docs**: (Auto-generated após EPIC-02)

---

**Document Owner**: @pm (Morgan)
**Last Updated**: 2026-01-28
**Version**: 1.0

*"Planejando o futuro 📊"*