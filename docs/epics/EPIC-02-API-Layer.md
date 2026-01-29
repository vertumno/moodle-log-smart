# Epic 2: API Layer Simplificada

**Epic ID**: EPIC-02
**Product**: MoodleLogSmart
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 2
**Duration**: 3-4 dias
**Status**: Not Started
**Epic Owner**: @dev
**Dependencies**: EPIC-01 (Backend Core)

---

## 📋 Epic Overview

### Epic Goal
Criar **API REST minimalista** com 3 endpoints apenas (upload, status, download) para conectar frontend ao pipeline de processamento.

### Business Value
- **Habilita interface web**: Frontend pode chamar backend
- **Experiência fluida**: Status em tempo real via polling
- **Simplicidade**: 3 endpoints cobrem todo fluxo

### Success Criteria
- ✅ API aceita upload CSV (multipart/form-data)
- ✅ API retorna status de processamento (%)
- ✅ API serve ZIP de resultados para download
- ✅ OpenAPI docs geradas automaticamente
- ✅ CORS configurado corretamente

---

## 👥 User Stories

### Story 2.1: Endpoint de Upload
**As a** frontend
**I want** enviar CSV via POST
**So that** backend processe o arquivo

**Acceptance Criteria**:
- ✅ POST `/api/upload` aceita multipart/form-data
- ✅ Valida arquivo é .csv (rejeita outros)
- ✅ Limita tamanho a 50MB
- ✅ Retorna job_id único
- ✅ Resposta JSON: `{"job_id": "uuid", "status": "processing"}`

**Tasks**:
- [ ] Setup FastAPI app
- [ ] Implementar `/api/upload` endpoint
- [ ] Validação de arquivo (mimetype, tamanho)
- [ ] Gerar job_id (uuid4)
- [ ] Iniciar processamento em background
- [ ] Adicionar tests de API

**Estimate**: 1 dia

---

### Story 2.2: Endpoint de Status
**As a** frontend
**I want** consultar progresso do job
**So that** posso mostrar progress bar ao usuário

**Acceptance Criteria**:
- ✅ GET `/api/status/{job_id}` retorna status atual
- ✅ Resposta JSON: `{"job_id": "uuid", "status": "processing", "progress": 45}`
- ✅ Status possíveis: "processing", "completed", "failed"
- ✅ Progress: 0-100 (percentual)
- ✅ Retorna 404 se job_id não existe

**Tasks**:
- [ ] Implementar `/api/status/{job_id}` endpoint
- [ ] Job tracking em memória (dict)
- [ ] Atualizar progress durante pipeline
- [ ] Error handling (job não encontrado)
- [ ] Adicionar tests de API

**Estimate**: 1 dia

---

### Story 2.3: Endpoint de Download
**As a** frontend
**I want** baixar ZIP de resultados
**So that** usuário receba os arquivos processados

**Acceptance Criteria**:
- ✅ GET `/api/download/{job_id}` retorna ZIP file
- ✅ Content-Type: application/zip
- ✅ Header: Content-Disposition com filename
- ✅ Retorna 404 se job não completou
- ✅ Arquivo temporário deletado após download

**Tasks**:
- [ ] Implementar `/api/download/{job_id}` endpoint
- [ ] Servir arquivo ZIP (FileResponse)
- [ ] Configurar headers corretos
- [ ] Cleanup de arquivos temporários
- [ ] Adicionar tests de API

**Estimate**: 1 dia

---

### Story 2.4: Job Management & Error Handling
**As a** sistema
**I want** gerenciar jobs em memória
**So that** múltiplos usuários possam processar logs

**Acceptance Criteria**:
- ✅ Dict em memória: `{job_id: JobState}`
- ✅ JobState: {status, progress, result_path, error}
- ✅ Timeout: jobs >10min são marcados como failed
- ✅ Cleanup: jobs completados >1h são removidos
- ✅ Error messages são user-friendly

**Tasks**:
- [ ] Implementar JobManager class
- [ ] Tracking de estado (dict)
- [ ] Timeout mechanism
- [ ] Cleanup background task
- [ ] Error handling middleware

**Estimate**: 0.5 dia

---

## 🏗️ Technical Architecture

### API Endpoints

```
POST   /api/upload
GET    /api/status/{job_id}
GET    /api/download/{job_id}
```

### Request/Response Examples

**1. Upload**
```bash
POST /api/upload
Content-Type: multipart/form-data

file: moodle_log.csv

→ Response 200:
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "message": "File uploaded successfully"
}
```

**2. Status**
```bash
GET /api/status/a1b2c3d4-e5f6-7890-abcd-ef1234567890

→ Response 200:
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "progress": 67,
  "message": "Enriching activities..."
}

→ Response 200 (completed):
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "progress": 100,
  "message": "Processing complete"
}

→ Response 404:
{
  "detail": "Job not found"
}
```

**3. Download**
```bash
GET /api/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890

→ Response 200:
Content-Type: application/zip
Content-Disposition: attachment; filename=results_20260128_153045.zip

[binary ZIP data]

→ Response 404:
{
  "detail": "Results not ready or job not found"
}
```

---

## 📁 File Structure

```
backend/
├── src/moodlelogsmart/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── routes.py            # 3 endpoints (arquivo único)
│   │   ├── schemas.py           # Pydantic models
│   │   ├── job_manager.py       # Job tracking
│   │   └── middleware.py        # Error handling, CORS
│   └── ...
```

---

## 🧪 Testing Strategy

### API Tests
- **Upload endpoint**: 5 test cases
  - Valid CSV upload
  - Invalid file type (rejected)
  - File too large (rejected)
  - Multiple uploads
  - Concurrent uploads

- **Status endpoint**: 4 test cases
  - Status during processing
  - Status after completion
  - Status after failure
  - Job not found (404)

- **Download endpoint**: 3 test cases
  - Download completed job
  - Download before completion (404)
  - Download expired job (404)

---

## ✅ Definition of Done

- ✅ 3 endpoints implementados e funcionais
- ✅ OpenAPI docs disponíveis em `/docs`
- ✅ CORS configurado
- ✅ Tests de API >80% coverage
- ✅ Error handling robusto
- ✅ Integration test: upload → status → download

---

**Epic Owner**: @dev
**Reviewer**: @architect
**Approver**: @pm (Morgan)