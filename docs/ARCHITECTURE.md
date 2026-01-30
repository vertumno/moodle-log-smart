# 🏗️ Arquitetura do Sistema

Documentação completa da arquitetura, design de componentes e fluxo de processamento do MoodleLogSmart.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura de Camadas](#arquitetura-de-camadas)
3. [Componentes Principais](#componentes-principais)
4. [Fluxo de Processamento](#fluxo-de-processamento)
5. [Estrutura de Dados](#estrutura-de-dados)
6. [Decisões Arquiteturais](#decisões-arquiteturais)

---

## 👀 Visão Geral

### Diagrama de Alto Nível

```
┌────────────────────────────────────────────────────────────────┐
│                         MOODLE LOG SMART                        │
├─────────────────────────┬──────────────────────────────────────┤
│                         │                                       │
│  FRONTEND (React/Vite)  │     BACKEND (FastAPI/Python)         │
│                         │                                       │
│  ┌──────────────────┐   │  ┌─────────────────────────────────┐ │
│  │  Web Interface   │   │  │   API Layer                     │ │
│  │  • Upload Zone   │◄──┼─►│   • /api/upload               │ │
│  │  • Progress Bar  │   │  │   • /api/status               │ │
│  │  • Download Btn  │◄──┼─►│   • /api/download             │ │
│  └──────────────────┘   │  └─────────────────────────────────┘ │
│        (HTTPS)          │              (HTTPS)                  │
│                         │                                       │
│     Vercel              │  ┌─────────────────────────────────┐ │
│     Deployment          │  │   Business Logic (Core)        │ │
│                         │  │  ┌─────────────────────────────┤ │
│                         │  │  │  Auto-Detection Engine      │ │
│                         │  │  │  • CSV Format Detection    │ │
│                         │  │  │  • Column Mapper           │ │
│                         │  │  │  • Timestamp Parser        │ │
│                         │  │  │                             │ │
│                         │  │  │  Data Cleaner             │ │
│                         │  │  │  • Filter by Role         │ │
│                         │  │  │  • Remove Duplicates      │ │
│                         │  │  │  • Normalize Data         │ │
│                         │  │  │                             │ │
│                         │  │  │  Bloom Classifier         │ │
│                         │  │  │  • 13 Semantic Rules      │ │
│                         │  │  │  • Taxonomy Levels (1-6)  │ │
│                         │  │  │  • Scoring System         │ │
│                         │  │  │                             │ │
│                         │  │  │  Multi-Format Exporter   │ │
│                         │  │  │  • CSV Export             │ │
│                         │  │  │  • XES Export (ProM)      │ │
│                         │  │  │  • ZIP Packaging          │ │
│                         │  │  └─────────────────────────────┤ │
│                         │  └─────────────────────────────────┘ │
│                         │                                       │
│                         │  ┌─────────────────────────────────┐ │
│                         │  │   Job Management                │ │
│                         │  │  • Async Processing Queue      │ │
│                         │  │  • State Tracking              │ │
│                         │  │  • 10min Job Timeout           │ │
│                         │  │  • TTL-based Cleanup (7 days)  │ │
│                         │  └─────────────────────────────────┘ │
│                         │                                       │
│                         │  Render Deployment                    │
│                         │  File System: /tmp/uploads, /tmp/jobs│
│                         │                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Arquitetura de Camadas

### Padrão: Clean Architecture + Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│                    (API / REST Endpoints)                       │
│  • FastAPI Routes                                               │
│  • Request/Response Validation (Pydantic)                       │
│  • Error Handling & HTTP Status Codes                           │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│               (Business Logic Orchestration)                    │
│  • Job Management (create, retrieve, delete)                    │
│  • Authentication & Authorization                              │
│  • File Upload Handling                                         │
│  • Async Task Coordination                                      │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BUSINESS LOGIC LAYER                        │
│                    (Domain Services / Core)                     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Auto-Detection Module                                  │  │
│  │  ├─ CSV Format Detection (encoding, delimiter)          │  │
│  │  ├─ Column Mapper (fuzzy matching to Moodle standard)   │  │
│  │  └─ Timestamp Parser (multiple date formats)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Data Cleaning Module                                   │  │
│  │  ├─ Role-based Filtering (students only)                │  │
│  │  ├─ Duplicate Removal                                   │  │
│  │  ├─ Data Validation & Normalization                     │  │
│  │  └─ Time Zone Handling                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Bloom Classification Module                            │  │
│  │  ├─ Rule Engine (13 semantic rules)                     │  │
│  │  ├─ Bloom Taxonomy Mapping (6 levels)                   │  │
│  │  ├─ Confidence Scoring                                  │  │
│  │  └─ Educational Event Classification                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Export Module                                          │  │
│  │  ├─ CSV Exporter                                        │  │
│  │  ├─ XES Exporter (ProM/Disco compatible)                │  │
│  │  ├─ ZIP Packager                                        │  │
│  │  └─ Metadata Generator                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                    (File System Access)                         │
│  • Temporary File Management (/tmp/uploads, /tmp/jobs)         │
│  • File I/O Operations                                         │
│  • Cleanup & TTL Management                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes Principais

### 1. Frontend (React/Vite)

**Localização**: `frontend/src/`

```
frontend/src/
├── components/
│   ├── UploadZone.tsx        # Drag-and-drop upload
│   ├── ProgressBar.tsx       # Real-time progress display
│   ├── DownloadButton.tsx    # Result download trigger
│   └── StatusMessage.tsx     # User feedback messages
│
├── hooks/
│   ├── useFileUpload.ts      # Upload state management
│   ├── useJobStatus.ts       # Poll job status
│   └── useApi.ts             # API client wrapper
│
├── services/
│   ├── api.ts                # Axios instance + endpoints
│   └── logger.ts             # Client-side logging
│
├── App.tsx                   # Main component
├── main.tsx                  # Entry point
└── index.css                 # Global styles (Tailwind)
```

**Stack**:
- React 18+ (hooks, functional components)
- TypeScript (type safety)
- Vite (fast development, optimized builds)
- Tailwind CSS (utility-first styling)
- Axios (HTTP client)

**Key Features**:
- Responsive design (mobile-friendly)
- Real-time progress updates
- Auto-refresh status polling
- Error handling & user feedback

### 2. Backend API Layer (FastAPI)

**Localização**: `backend/src/moodlelogsmart/api/`

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI(
    title="MoodleLogSmart API",
    version="1.0.0",
    docs_url="/docs"
)

# Middleware
app.add_middleware(CORSMiddleware, ...)
app.add_middleware(TrustedHostMiddleware, ...)

# Routes
@app.post("/api/upload")
async def upload_file(file: UploadFile): ...

@app.get("/api/status/{job_id}")
async def get_status(job_id: str): ...

@app.get("/api/download/{job_id}")
async def download_results(job_id: str): ...
```

**Componentes**:

- `auth.py` - API Key authentication
- `models.py` - Pydantic request/response schemas
- `validators.py` - Input validation & sanitization
- `job_manager.py` - Job lifecycle management

**Middleware**:
- CORS (só permite frontend URL)
- Security Headers (CSP, X-Frame-Options, HSTS)
- Request logging & monitoring

### 3. Business Logic Core (Python)

**Localização**: `backend/src/moodlelogsmart/core/`

#### Auto-Detection Engine

```
auto_detect/
├── csv_detector.py          # Encoding/delimiter detection
├── column_mapper.py         # Column mapping (fuzzy matching)
└── timestamp_detector.py    # Date format detection
```

**Detecção de Encoding**:
- Tenta: UTF-8, ISO-8859-1, cp1252
- Charset detection via library
- Fallback: força UTF-8

**Detecção de Delimiter**:
- Testa: `,`, `;`, `\t`, `|`
- Conta frequência
- Escolhe mais comum

**Mapeamento de Colunas**:
- Fuzzy matching com 80% threshold
- Suporta PT-BR e EN
- Moodle standard: userid, firstname, lastname, email, action, description, etc.

**Detecção de Timestamp**:
- Regex patterns para múltiplos formatos
- DD/MM/YYYY, YYYY-MM-DD, Unix timestamp
- ISO 8601, etc.

#### Data Cleaner

```
clean/
└── data_cleaner.py
```

**Operações**:
1. Filter by role (apenas students)
2. Remove invalid rows
3. Deduplicate events
4. Normalize timestamps (ISO 8601)
5. Validate data types

#### Bloom Classifier

```
rules/
├── rule_engine.py           # 13 semantic rules
└── bloom_classifier.py      # Taxonomy mapping
```

**13 Regras Semânticas**:
1. View action → Remember (Level 1)
2. Submit action → Apply (Level 3)
3. Essay question → Evaluate (Level 5)
4. Quiz attempt → Understand (Level 2)
5. Forum post → Analyze (Level 4)
6. Peer review → Create (Level 6)
... (13 total)

**Scoring**:
- Confidence 0.0-1.0
- Higher score = more confident
- Used for filtering in "bloom_only" export

#### Exporter

```
export/
└── exporter.py              # CSV, XES, ZIP output
```

**Formatos**:
- CSV (enriquecido com Bloom)
- CSV (apenas eventos pedagógicos)
- XES (ProM/Disco compatible)
- XES (apenas eventos pedagógicos)
- ZIP (contendo todos)

### 4. Job Management

**Localização**: `backend/src/moodlelogsmart/api/job_manager.py`

```python
class JobManager:
    """Gerencia ciclo de vida de jobs de processamento."""

    async def create_job(self, file: UploadFile) -> str:
        """Cria novo job e inicia processamento."""
        job_id = generate_uuid()
        self.jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "file_path": save_temp_file(file),
            "created_at": datetime.now()
        }
        asyncio.create_task(self._process_job(job_id))
        return job_id

    async def get_status(self, job_id: str) -> dict:
        """Retorna status atual do job."""
        if job_id not in self.jobs:
            raise JobNotFound()
        return self.jobs[job_id]

    async def delete_job(self, job_id: str):
        """Deleta job e limpa arquivos."""
        job = self.jobs.pop(job_id)
        cleanup_files(job["file_path"])

    async def cleanup_expired_jobs(self):
        """TTL-based cleanup: 7 dias de retenção."""
        now = datetime.now()
        for job_id, job in list(self.jobs.items()):
            if (now - job["created_at"]).days >= 7:
                await self.delete_job(job_id)
```

**Estados de Job**:
```
queued → processing → completed
                   ├→ failed
                   └→ timeout
```

**Timeout**: 10 minutos por job
**Cleanup**: Executado a cada 1 hora
**Retenção**: 7 dias após conclusão

---

## 🔄 Fluxo de Processamento

### Fluxo Completo: Upload → Processing → Download

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Select CSV File │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Drag or Click   │
                    └────────┬────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND ACTION                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  POST /api/upload                                               │
│  Content-Type: multipart/form-data                             │
│  X-API-Key: ...                                                │
│  Body: {file: File}                                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                        API HANDLER                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Validar API Key ✓                                           │
│  2. Validar arquivo (size, type) ✓                             │
│  3. Salvar em /tmp/uploads/... ✓                               │
│  4. Criar job_id (UUID) ✓                                      │
│  5. Iniciar processamento assíncrono ✓                         │
│  6. Retornar {job_id, status: "queued"} ✓                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    BACKGROUND PROCESSING                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ETAPA 1: Auto-Detection (5%)                                   │
│  ├─ Detectar encoding                                           │
│  ├─ Detectar delimiter                                          │
│  ├─ Mapear colunas (fuzzy match)                               │
│  └─ Detectar timestamp format                                  │
│                                                                  │
│  ETAPA 2: Limpeza (20%)                                         │
│  ├─ Ler CSV completo                                           │
│  ├─ Filtrar por role (estudantes)                             │
│  ├─ Validar dados                                              │
│  └─ Remover duplicatas                                         │
│                                                                  │
│  ETAPA 3: Enriquecimento (40%)                                  │
│  ├─ Aplicar 13 regras semânticas                               │
│  ├─ Classificar com Bloom (levels 1-6)                         │
│  ├─ Calcular scores de confiança                               │
│  └─ Marcar eventos pedagógicos                                 │
│                                                                  │
│  ETAPA 4: Exportação (25%)                                      │
│  ├─ Gerar CSV enriquecido                                      │
│  ├─ Gerar CSV bloom_only                                       │
│  ├─ Gerar XES (ProM format)                                    │
│  ├─ Gerar XES bloom_only                                       │
│  └─ Gerar metadata.json                                        │
│                                                                  │
│  ETAPA 5: Packaging (10%)                                       │
│  ├─ Criar ZIP contendo todos os arquivos                       │
│  ├─ Mover para /tmp/jobs/{job_id}/                            │
│  └─ Atualizar status: "completed"                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND POLLING                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Intervalo: a cada 2 segundos                                  │
│  GET /api/status/{job_id}                                      │
│  X-API-Key: ...                                                │
│                                                                  │
│  Resposta: {                                                    │
│    "status": "processing",                                      │
│    "progress": 45,                                              │
│    "message": "Enriquecendo com Bloom..."                       │
│  }                                                              │
│                                                                  │
│  Atualizar UI:                                                 │
│  └─ Progress bar: 45%                                           │
│  └─ Mensagem de status                                          │
│                                                                  │
│  Quando "status" == "completed":                               │
│  └─ Mostrar botão "Download"                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DOWNLOAD REQUEST                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GET /api/download/{job_id}                                    │
│  X-API-Key: ...                                                │
│                                                                  │
│  Resposta:                                                     │
│  ├─ Content-Type: application/zip                             │
│  ├─ Content-Disposition: attachment; filename="...zip"        │
│  └─ [arquivo ZIP binário]                                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Arquivo ZIP Baixado  │
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Extrair ZIP          │
                   ├──────────────────────┤
                   │ • enriched_log.csv   │
                   │ • bloom_only.csv     │
                   │ • enriched_log.xes   │
                   │ • bloom_only.xes     │
                   │ • metadata.json      │
                   └──────────────────────┘
```

---

## 📊 Estrutura de Dados

### Job Object

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "created_at": "2024-01-15T10:30:45.123456Z",
  "updated_at": "2024-01-15T10:32:45.123456Z",
  "completed_at": "2024-01-15T10:32:45.123456Z",
  "file_path": "/tmp/uploads/550e8400-.../original.csv",
  "output_path": "/tmp/jobs/550e8400-.../results.zip",
  "error": null,
  "statistics": {
    "total_events": 5000,
    "student_events": 4800,
    "bloom_classified": 3500,
    "invalid_events": 200,
    "processing_time_seconds": 120
  }
}
```

### Log Entry (with Bloom Classification)

```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "userid": 123,
  "action": "submit",
  "component": "quiz",
  "description": "User submitted quiz 'Chapter 1 Test'",
  "bloom_level": 3,
  "bloom_category": "apply",
  "bloom_score": 0.87,
  "is_pedagogical": true,
  "matched_rule": "RULE_003_QUIZ_SUBMIT"
}
```

### Bloom Levels

```python
BLOOM_LEVELS = {
    1: "Remember",    # Recall facts, definitions
    2: "Understand",  # Explain ideas, concepts
    3: "Apply",       # Use information in new situations
    4: "Analyze",     # Draw connections among ideas
    5: "Evaluate",    # Justify a stand or decision
    6: "Create"       # Produce new or original work
}
```

---

## 🎯 Decisões Arquiteturais

### 1. Por que FastAPI?

**Escolha**: FastAPI + Uvicorn

**Razões**:
- Validação automática com Pydantic
- Documentação interativa (Swagger)
- Async/await nativo (melhor performance)
- Type hints support (melhor IDE)
- Rápido de desenvolver e debugar

### 2. Por que React?

**Escolha**: React 18 + TypeScript + Vite

**Razões**:
- Component-based architecture
- Rich ecosystem (hooks, testing tools)
- TypeScript para type safety
- Vite para fast builds & dev server
- SSG/SSR capaz quando necessário

### 3. Por que File System em vez de Database?

**Escolha**: /tmp/uploads e /tmp/jobs

**Razões**:
- MVP não requer persistência
- Simpler deployment (Render suporta /tmp)
- Fast I/O
- Evita dependency de banco de dados
- TTL-based cleanup funciona bem para temp files

**Futuro**: Migrar para PostgreSQL se necessário

### 4. Por que ZIP Export?

**Escolha**: Múltiplos formatos em ZIP

**Razões**:
- Mantém tudo junto
- Reduz tamanho (compressão)
- Fácil distribuição
- Users podem usar qualquer arquivo
- Metadata.json para tracking

### 5. Por que 13 Regras Semânticas?

**Escolha**: Rule-based taxonomy em vez de ML

**Razões**:
- Determinístico e reproduzível
- Fácil de debugar e iterar
- Não requer training data
- Explicável (rule 3 = quiz → apply)
- Customizável por educador

### 6. Por que Async Processing?

**Escolha**: AsyncIO + Background tasks

**Razões**:
- Não bloqueia servidor
- Multi-job simultâneo
- Melhor utilização de recursos
- UI responsiva (status polling)
- Timeout protection (10 min)

### 7. Por que Vercel + Render?

**Escolha**: Serverless + Container

**Razões**:
- Vercel: Zero-config React deployments
- Render: Python-friendly, simple setup
- Ambos: Auto-scaling, monitoring, logs
- Ambos: GitHub integration
- Custo: Free/cheap tier disponível

---

## 🔐 Segurança

### Camadas de Proteção

```
┌─────────────────────────────────────────┐
│ Browser                                 │
│ ├─ CORS Policy                         │
│ └─ Content-Security-Policy             │
├─────────────────────────────────────────┤
│ API Gateway                             │
│ ├─ HTTPS/TLS                           │
│ ├─ Rate Limiting                       │
│ └─ DDoS Protection                     │
├─────────────────────────────────────────┤
│ Application Layer                       │
│ ├─ API Key Authentication              │
│ ├─ Job Ownership Enforcement           │
│ ├─ Input Validation (Pydantic)        │
│ └─ Error Handling (no sensitive info) │
├─────────────────────────────────────────┤
│ File Handling                           │
│ ├─ UUID Validation (path traversal)    │
│ ├─ CSV Injection Prevention            │
│ ├─ File Size Limits                    │
│ └─ Temporary File Cleanup              │
├─────────────────────────────────────────┤
│ Infrastructure                          │
│ ├─ Non-root Container Execution        │
│ ├─ Environment Variable Secrets         │
│ └─ Regular Security Updates            │
└─────────────────────────────────────────┘
```

### Exemplo: UUID Validation

```python
import uuid

def validate_job_id(job_id: str) -> bool:
    """Prevent path traversal attacks."""
    try:
        uuid.UUID(job_id)
        return True
    except ValueError:
        return False

# Uso
@app.get("/api/download/{job_id}")
async def download(job_id: str):
    if not validate_job_id(job_id):
        raise HTTPException(status_code=400, detail="Invalid job_id")
    # Seguro contra: /api/download/../../../../etc/passwd
```

---

## 📈 Performance Characteristics

### Benchmarks

| Métrica | Valor |
|---------|-------|
| **Upload (50MB)** | <5s |
| **Auto-Detection** | <1s |
| **Data Cleaning** | ~10s (per 5000 events) |
| **Bloom Enrichment** | ~80s (5000 events) |
| **Export** | ~10s (all formats) |
| **API Response** | <200ms (avg) |
| **Total Processing** | <2 min (5000 events) |

### Scalability

**Vertical**:
- Render: CPU/Memory upgrade
- Vercel: Auto-scales functions

**Horizontal**:
- Multiple backend instances (future)
- Load balancing (future)
- Database sharding (future)

---

## 🔄 CI/CD Pipeline

```
GitHub Push
    │
    ├─→ [main branch]
    │   ├─→ Run Tests (pytest, npm test)
    │   ├─→ Lint & Format (Black, ESLint)
    │   ├─→ Type Check (mypy, TypeScript)
    │   ├─→ Deploy to Staging
    │   │   ├─→ Vercel Preview
    │   │   └─→ Render Staging
    │   └─→ Run E2E Tests
    │
    └─→ [v*.*.* tag]
        └─→ Deploy to Production
            ├─→ Vercel Production
            └─→ Render Production
```

---

## 📚 Recursos Relacionados

- [API.md](./API.md) - Endpoints REST
- [DEPLOYMENT.md](../DEPLOYMENT.md) - Deploy guide
- [PROJECT-STATUS.md](../PROJECT-STATUS.md) - Progress dashboard

---

**Última Atualização**: 2026-01-30

**Arquitetura Versão**: 1.0.0
