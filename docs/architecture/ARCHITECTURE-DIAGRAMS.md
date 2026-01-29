# 🏗️ MoodleLogSmart - Diagramas de Arquitetura

## 1️⃣ Diagrama C4 - System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                      MoodleLogSmart System                       │
│                                                                   │
│  Usuário (Pesquisador Educacional)                              │
│         │                                                         │
│         ├─ Acessa interface web                                 │
│         ├─ Faz upload de CSV do Moodle                          │
│         └─ Baixa ZIP com resultados enriquecidos               │
│         │                                                         │
│    ┌────▼─────────────────────────────────────────────────┐     │
│    │                                                       │     │
│    │         📱 Web Interface (React)                     │     │
│    │    ┌─────────────────────────────────────┐           │     │
│    │    │ - Upload (Drag & Drop)              │           │     │
│    │    │ - Progress Bar (Real-time)          │           │     │
│    │    │ - Download Button (ZIP)             │           │     │
│    │    └─────────────────────────────────────┘           │     │
│    │                 │                                     │     │
│    │         REST API (HTTP/HTTPS)                        │     │
│    │                 │                                     │     │
│    │    ┌────────────▼─────────────────────────────────┐  │     │
│    │    │                                              │  │     │
│    │    │      🔧 FastAPI Backend                      │  │     │
│    │    │                                              │  │     │
│    │    │  ┌──────────────────────────────────────┐   │  │     │
│    │    │  │ POST /api/upload → process CSV       │   │  │     │
│    │    │  │ GET /api/status/{job_id}             │   │  │     │
│    │    │  │ GET /api/download/{job_id} → ZIP    │   │  │     │
│    │    │  └──────────────────────────────────────┘   │  │     │
│    │    │                                              │  │     │
│    │    │  Processing Pipeline:                       │  │     │
│    │    │  1️⃣ Auto-Detect (CSV format)             │  │     │
│    │    │  2️⃣ Clean (Filter by role)               │  │     │
│    │    │  3️⃣ Enrich (Bloom rules)                 │  │     │
│    │    │  4️⃣ Export (CSV + XES)                   │  │     │
│    │    │  5️⃣ Package (ZIP)                        │  │     │
│    │    └──────────────────────────────────────────┘   │     │
│    │                                                       │     │
│    └───────────────────────────────────────────────────────┘     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

Sistema Externo: Moodle
  └─ Exporta logs como CSV
     (encoding variável, delimiters, formatos de timestamp diferentes)
```

---

## 2️⃣ Diagrama C4 - Containers

```
┌──────────────────────────────────────────────────────────────────┐
│                    MoodleLogSmart - Containers                   │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐     ┌──────────────────────────┐
│   Frontend Container        │     │  Backend Container       │
│   (React + TypeScript)      │     │  (Python + FastAPI)      │
│                             │     │                          │
│  • UploadZone.tsx           │     │  • Auto-Detection Core   │
│  • ProgressBar.tsx          │────▶│  • Data Cleaning        │
│  • DownloadButton.tsx       │     │  • Enrichment Engine    │
│  • API Client (fetch)       │     │  • Exporters (CSV/XES)  │
│                             │     │  • Job Manager          │
│  Runs on: http://localhost  │     │  • API Routes           │
│           :3000             │     │                          │
│                             │     │  Runs on: http://localhost
└─────────────────────────────┘     │           :8000
         │                           │
         │ HTTP/HTTPS               │
         │ (REST API)               └──────────────────────────┘
         │                                    │
         │◀──────────────────────────────────▶│
         │                                    │
    JSON Request/Response              File I/O
    • upload(CSV)                    • Read CSV
    • status(job_id)                 • Write CSV/XES
    • download(job_id)               • Create ZIP
         │                                    │
         │                          ┌─────────▼──────────┐
         │                          │  File Storage      │
         │                          │                    │
         │                          │ /uploads/          │
         │                          │ /processing/       │
         │                          │ /results/          │
         │                          │ /temp/             │
         │                          └────────────────────┘
         │
    ┌────▼──────────────────────────────────────┐
    │  Browser (User's Machine)                  │
    │  • Cache results                           │
    │  • Download ZIP                            │
    └─────────────────────────────────────────────┘
```

---

## 3️⃣ Diagrama C4 - Components (Backend - Core)

```
BACKEND ARCHITECTURE - LAYERED

┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  (FastAPI Routes)                                            │
│  • POST /api/upload → CSVDetector → Job Creation           │
│  • GET /api/status/{id} → Job Manager                       │
│  • GET /api/download/{id} → ZIPPackager                     │
└─────────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────▼──────────────────────────────────┐
│               APPLICATION LAYER (Pipeline)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Processing Pipeline                                 │  │
│  │  ┌─────────────┐     ┌─────────────┐     ┌─────────┐│  │
│  │  │ Detect Step │ ──▶ │ Clean Step  │ ──▶ │Enrich  ││  │
│  │  └─────────────┘     └─────────────┘     │Step   ││  │
│  │        │                    │             │      ││  │
│  │    CSV Detection        Role Filter    Bloom     ││  │
│  │    Timestamp Format     Event Filter   Rules    ││  │
│  │    Column Mapping       Normalize      Engine   ││  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Export Step                                       │  │
│  │ ├─ CSV Exporter (Pandas)                         │  │
│  │ ├─ XES Exporter (PM4Py)                          │  │
│  │ └─ ZIP Packager                                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────▼──────────────────────────────────┐
│                  DOMAIN LAYER (Entities)                    │
│                                                              │
│  ┌──────────────────┐    ┌─────────────────┐              │
│  │ RawMoodleEvent   │    │ EnrichedActivity│              │
│  │                  │    │                 │              │
│  │ • time           │    │ • time          │              │
│  │ • user_name      │    │ • user_name     │              │
│  │ • event_name     │    │ • event_name    │              │
│  │ • component      │ ──▶│ • activity_type │ ✨ Enriquecido
│  │ • description    │    │ • bloom_level   │              │
│  │                  │    │ • is_active     │              │
│  └──────────────────┘    │ • confidence    │              │
│                          └─────────────────┘              │
│                                                              │
│  Enums:                                                      │
│  • ActivityType: Study_P/A, Exercise_P/A, Assess_P/A,     │
│                 Synthesize, View, Feedback, Others         │
│  • BloomLevel: Remember, Understand, Apply, Analyze,      │
│               Evaluate, Create                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          │
┌─────────────────────────▼──────────────────────────────────┐
│            INFRASTRUCTURE LAYER (Data Access)               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ File System Storage                                 │    │
│  │                                                     │    │
│  │ /uploads/          → Input CSV files               │    │
│  │ /processing/       → Intermediate files            │    │
│  │ /results/          → Final outputs (CSV + XES)     │    │
│  │ /temp/             → Temporary processing data     │    │
│  │                                                     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4️⃣ Pipeline de Processamento (Fluxo de Dados)

```
INPUT (Usuário)
     │
     │ "moodle_log.csv"
     │ (encoding desconhecido, formato incerto)
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 1: AUTO-DETECTION                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CSVDetector                                            │
│  ├─ Detecta encoding (UTF-8, Latin-1, CP1252)         │
│  ├─ Detecta delimiter (,  ;  \t  |)                    │
│  ├─ Valida estrutura (tem header? tem dados?)          │
│  └─ Resultado: CSVFormat(encoding, delimiter, ...)     │
│                                                          │
│  ColumnMapper                                           │
│  ├─ Testa nomes de colunas Moodle conhecidas           │
│  ├─ Fuzzy matching (80% threshold)                     │
│  └─ Resultado: Mapeamento de colunas                   │
│                                                          │
│  TimestampDetector                                      │
│  ├─ Testa 12+ formatos comuns                          │
│  ├─ Fallback: pandas.to_datetime() inference           │
│  └─ Resultado: Formato de timestamp detectado          │
│                                                          │
└─────────────────────────────────────────────────────────┘
     │
     │ CSV lido com detecções aplicadas
     ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 2: DATA CLEANING                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  RoleFilter                                             │
│  ├─ Filtra: studentRoleID = "5" (padrão Moodle)       │
│  └─ Remove teachers, admins, etc                       │
│                                                          │
│  EventFilter                                            │
│  ├─ Remove eventos não-estudantis                      │
│  ├─ Lista: "Course updated", "Backup created", etc     │
│  └─ Mantém apenas atividades pedagógicas               │
│                                                          │
│  TimestampValidator                                     │
│  ├─ Remove timestamps inválidos                        │
│  ├─ Valida range (2000 até now+1)                      │
│  └─ Normaliza para UTC                                 │
│                                                          │
│  DataNormalizer                                         │
│  ├─ Normaliza tipos de dados                           │
│  ├─ Limpa strings (trim whitespace)                    │
│  └─ Padroniza format de saída                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
     │
     │ DataFrame limpo (apenas eventos de estudantes)
     ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 3: SEMANTIC ENRICHMENT                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  RuleEngine (bloom_taxonomy.yaml)                       │
│  ├─ Carrega 13 regras de classificação                 │
│  ├─ Para cada evento:                                  │
│  │  ├─ Testa condições (equals, in, contains)         │
│  │  ├─ Prioridade: regra específica ganha             │
│  │  └─ Aplica ação: activity_type + bloom_level       │
│  └─ Fallback: "Others" se nenhuma regra match         │
│                                                          │
│  Exemplo de Regra:                                      │
│  Rule 1: "View Resource"                               │
│    IF component IN ["File", "Folder", "Page"]          │
│    AND event_name = "Course module viewed"             │
│    THEN activity_type = "Study_P", bloom = "Remember" │
│                                                          │
│  BloomClassifier (wrapper)                             │
│  ├─ Adiciona colunas: activity_type, bloom_level      │
│  ├─ Adiciona: is_active (true/false)                  │
│  └─ Adiciona: confidence_score (0.0 - 1.0)            │
│                                                          │
└─────────────────────────────────────────────────────────┘
     │
     │ DataFrame enriquecido com classificação semântica
     ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 4: EXPORT (Múltiplos Formatos)                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CSVExporter                                            │
│  ├─ Exporta enriched_log.csv (completo)               │
│  └─ Exporta enriched_log_bloom_only.csv (pedagogia)   │
│                                                          │
│  XESExporter (PM4Py)                                    │
│  ├─ Exporta enriched_log.xes (completo)               │
│  └─ Exporta enriched_log_bloom_only.xes               │
│  ├─ Formato: XML Process Mining                        │
│  └─ Compatível: ProM, Disco, CyberOps                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
     │
     │ 4 arquivos gerados (CSV + XES, 2 versões cada)
     ▼
┌─────────────────────────────────────────────────────────┐
│ STEP 5: PACKAGING                                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ZIPPackager                                            │
│  ├─ Empacota os 4 arquivos                             │
│  ├─ Nome: results_YYYYMMDD_HHMMSS.zip                 │
│  ├─ Compressão: ZIP_DEFLATED                           │
│  └─ Validação: arquivo extraível                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
     │
     │ results_20240128_153045.zip
     ▼
OUTPUT (Usuário)
     └─ Download ZIP contendo:
        ├─ enriched_log.csv (com colunas activity_type, bloom_level)
        ├─ enriched_log_bloom_only.csv (pedagogia apenas)
        ├─ enriched_log.xes (completo, PM4Py format)
        └─ enriched_log_bloom_only.xes (pedagogia apenas)
```

---

## 5️⃣ Diagrama de Dependências (Story Sequencing)

```
EPIC 01: Backend Core + Auto-Detection (Sprint 1)

    ┌─────────────────────────────────────────────┐
    │ STORY 1.1: CSV Auto-Detection               │
    │ (CSVDetector - encoding, delimiter)         │
    │ Estimate: 1 dia | Status: ⏳ Not Started  │
    └────────────────┬────────────────────────────┘
                     │
                     │ Blocks ▼
    ┌────────────────────────────────┬──────────────────┐
    │                                │                  │
    │ STORY 1.2:                     │ STORY 1.3:      │
    │ Column Mapping                 │ Timestamp Detection
    │ (ColumnMapper)                 │ (TimestampDetector)
    │ Estimate: 1 dia                │ Estimate: 1 dia
    └────────────────┬───────────────┴────────────┬──────┘
                     │                            │
                     └────────────┬───────────────┘
                                  │ Both block ▼
                     ┌────────────────────────────────────┐
                     │ STORY 1.4: Data Cleaning           │
                     │ (RoleFilter, EventFilter, etc)     │
                     │ Estimate: 1 dia | Day 3            │
                     └────────────────┬───────────────────┘
                                      │ Blocks ▼
                     ┌────────────────────────────────────┐
                     │ STORY 1.5: Rule Engine + Bloom     │
                     │ (RuleEngine, BloomClassifier)      │
                     │ Estimate: 2 dias | Day 4           │
                     └────────────────┬───────────────────┘
                                      │ Blocks ▼
                     ┌────────────────────────────────────┐
                     │ STORY 1.6: Export (CSV + XES)      │
                     │ (CSVExporter, XESExporter)         │
                     │ Estimate: 1 dia | Day 5            │
                     └────────────────┬───────────────────┘
                                      │ Blocks ▼
                     ┌────────────────────────────────────┐
                     │ STORY 1.7: ZIP Packager            │
                     │ (ZIPPackager)                      │
                     │ Estimate: 0.5 dia | Day 5          │
                     └────────────────┬───────────────────┘
                                      │ Produces ▼
                     ┌────────────────────────────────────┐
                     │ ✅ EPIC 01 COMPLETE                 │
                     │ Pipeline: CSV → ZIP (4 arquivos)   │
                     │ Auto-detection funcional           │
                     └────────────────────────────────────┘
```

---

## 6️⃣ Diagrama de Estados (Job Processing)

```
JOB LIFECYCLE

┌──────────────┐
│   CREATED    │  Usuário faz upload
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│   DETECTING              │  Detectando CSV format
│   (CSVDetector)          │  Estimado: 1-2 segundos
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   CLEANING               │  Filtrando + Normalizando
│   (RoleFilter, etc)      │  Estimado: 2-5 segundos
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   ENRICHING              │  Aplicando regras Bloom
│   (RuleEngine)           │  Estimado: 3-10 segundos (depende de volume)
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   EXPORTING              │  Escrevendo CSV + XES
│   (Exporters)            │  Estimado: 1-3 segundos
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   PACKAGING              │  Criando ZIP
│   (ZIPPackager)          │  Estimado: 1-2 segundos
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   COMPLETED ✅           │  Pronto para download
│   Tempo Total:           │  ~10-25 segundos típico
│   (1000-5000 eventos)    │
└──────────────────────────┘

Erro em qualquer passo:
       ▼
┌──────────────────────────┐
│   FAILED ❌              │
│   Mensagem de erro       │
│   Usuário tenta novamente│
└──────────────────────────┘
```

---

## 7️⃣ Diagrama de Pastas (Estrutura do Repositório)

```
moodlelogsmart/
│
├── 📁 backend/
│   ├── 📁 src/moodlelogsmart/
│   │   ├── 📁 api/
│   │   │   ├── main.py                      ← FastAPI app
│   │   │   ├── routes.py                    ← 3 endpoints
│   │   │   └── schemas/
│   │   │       └── job.py                   ← Job request/response
│   │   │
│   │   ├── 📁 domain/
│   │   │   ├── entities/
│   │   │   │   ├── event.py                 ← RawMoodleEvent, EnrichedActivity
│   │   │   │   ├── csv_format.py            ← CSVFormat
│   │   │   │   └── rule.py                  ← Rule entities
│   │   │   └── enums.py                     ← ActivityType, BloomLevel
│   │   │
│   │   ├── 📁 core/
│   │   │   ├── 📁 auto_detect/
│   │   │   │   ├── csv_detector.py          ⭐ STORY-1.1
│   │   │   │   ├── column_mapper.py         ⭐ STORY-1.2
│   │   │   │   └── timestamp_detector.py    ⭐ STORY-1.3
│   │   │   │
│   │   │   ├── 📁 cleaning/
│   │   │   │   ├── role_filter.py           ⭐ STORY-1.4
│   │   │   │   ├── event_filter.py          ⭐ STORY-1.4
│   │   │   │   ├── timestamp_validator.py   ⭐ STORY-1.4
│   │   │   │   └── normalizer.py            ⭐ STORY-1.4
│   │   │   │
│   │   │   ├── 📁 enrichment/
│   │   │   │   ├── rule_engine.py           ⭐ STORY-1.5
│   │   │   │   └── bloom_classifier.py      ⭐ STORY-1.5
│   │   │   │
│   │   │   └── 📁 export/
│   │   │       ├── csv_exporter.py          ⭐ STORY-1.6
│   │   │       ├── xes_exporter.py          ⭐ STORY-1.6
│   │   │       └── zip_packager.py          ⭐ STORY-1.7
│   │   │
│   │   ├── 📁 pipeline/
│   │   │   ├── builder.py
│   │   │   └── processor.py                 ← Orquestra tudo
│   │   │
│   │   ├── 📁 config/
│   │   │   ├── settings.py                  ← Config (FastAPI)
│   │   │   └── defaults.py                  ← Defaults hard-coded
│   │   │
│   │   ├── 📁 job/
│   │   │   └── manager.py                   ← Job management em memória
│   │   │
│   │   └── __init__.py
│   │
│   ├── 📁 rules/
│   │   └── 📁 default/
│   │       └── bloom_taxonomy.yaml          ← 13 regras Bloom
│   │
│   ├── 📁 tests/
│   │   ├── 📁 unit/
│   │   │   ├── test_csv_detector.py
│   │   │   ├── test_column_mapper.py
│   │   │   ├── test_timestamp_detector.py
│   │   │   ├── test_role_filter.py
│   │   │   ├── test_rule_engine.py
│   │   │   ├── test_exporters.py
│   │   │   └── test_zip_packager.py
│   │   │
│   │   ├── 📁 integration/
│   │   │   ├── test_pipeline_e2e.py         ← Full pipeline test
│   │   │   └── fixtures/
│   │   │       └── moodle_log_sample.csv
│   │   │
│   │   └── conftest.py                      ← Pytest fixtures
│   │
│   ├── pyproject.toml                       ← Poetry dependencies
│   ├── poetry.lock
│   ├── Dockerfile
│   └── .dockerignore
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── UploadZone.tsx               ← Drag & drop
│   │   │   ├── ProgressBar.tsx              ← Barra de progresso
│   │   │   └── DownloadButton.tsx           ← Download button
│   │   │
│   │   ├── 📁 services/
│   │   │   └── api.ts                       ← HTTP client
│   │   │
│   │   ├── App.tsx                          ← Página única
│   │   ├── main.tsx                         ← Entry point
│   │   └── index.css                        ← Tailwind
│   │
│   ├── 📁 public/
│   │   └── index.html
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── .dockerignore
│
├── 📁 docs/
│   ├── 📁 architecture/                     👈 You are here
│   │   ├── ARCHITECTURE-DIAGRAMS.md
│   │   ├── ARCHITECTURE-DECISIONS.md
│   │   └── API-SPECIFICATION.md
│   │
│   ├── 📁 stories/
│   │   ├── README.md
│   │   ├── STORY-1.1-Auto-Detection-CSV-Format.md
│   │   ├── STORY-1.2-Auto-Mapping-Moodle-Columns.md
│   │   ├── STORY-1.3-Auto-Detection-Timestamp-Format.md
│   │   └── STORY-1.4-to-1.7-Remaining-Epic01.md
│   │
│   ├── 📁 epics/
│   │   ├── README.md
│   │   ├── EPIC-01-Backend-Core-AutoDetection.md
│   │   ├── EPIC-02-API-Layer.md
│   │   ├── EPIC-03-Frontend-Minimalista.md
│   │   └── EPIC-04-Docker-Deployment.md
│   │
│   ├── PRD-MoodleLogSmart.md
│   └── README.md
│
├── docker-compose.yml
├── .gitignore
├── .github/
│   └── 📁 workflows/
│       ├── ci.yml
│       ├── tests.yml
│       └── deploy.yml
│
├── README.md                                ← Quick start
├── LICENSE
└── .env.example
```

---

## 8️⃣ Diagrama de Data Models

```
RawMoodleEvent (Input)
┌─────────────────────────────────────┐
│ Field              │ Type          │
├────────────────────┼──────────────┤
│ time               │ datetime      │
│ user_full_name     │ str           │
│ event_context      │ str (course)  │
│ component          │ str (module)  │
│ event_name         │ str (action)  │
│ description        │ str           │
│ affected_user      │ str | None    │
│ origin             │ str | None    │
│ ip_address         │ str | None    │
└─────────────────────────────────────┘
         │
         │ Processing
         ▼
EnrichedActivity (Output)
┌─────────────────────────────────────┐
│ Field              │ Type          │
├────────────────────┼──────────────┤
│ [campos originais]  │ (todos acima) │
│                    │               │
│ activity_type      │ ActivityType  │✨ NOVO
│ bloom_level        │ BloomLevel    │✨ NOVO
│ is_active          │ bool          │✨ NOVO
│ confidence_score   │ float (0-1.0) │✨ NOVO
│ rule_applied       │ str | None    │✨ NOVO
│ case_id            │ str           │✨ NOVO
│ activity_name      │ str           │✨ NOVO
│ resource           │ str           │✨ NOVO
└─────────────────────────────────────┘

ActivityType Enum:
  ├─ Study_P (Passivo: ler, visualizar)
  ├─ Study_A (Ativo: completou leitura)
  ├─ Exercise_P (Passivo: viu exercício)
  ├─ Exercise_A (Ativo: submeteu resposta)
  ├─ Assess_P (Passivo: viu avaliação)
  ├─ Assess_A (Ativo: completou avaliação)
  ├─ Synthesize (Ativo: criou conteúdo)
  ├─ View (Não-pedagógico: apenas visualização)
  ├─ Feedback (Não-pedagógico: feedback)
  ├─ Interact (Não-pedagógico: chat, forum)
  └─ Others (Não-pedagógico: outros)

BloomLevel Enum:
  ├─ Remember (1 - Recuperar informação)
  ├─ Understand (2 - Explicar ideias/conceitos)
  ├─ Apply (3 - Usar informação em situação nova)
  ├─ Analyze (4 - Distinguir partes, relações)
  ├─ Evaluate (5 - Justificar uma posição/decisão)
  └─ Create (6 - Produzir novo produto/ponto de vista)
```

---

## 9️⃣ Stack Tecnológico (Decisões Arquiteturais)

```
BACKEND STACK
├─ Linguagem: Python 3.11+
│  └─ Razão: Data science libs, processamento de arquivos, prototipagem rápida
├─ Framework: FastAPI
│  └─ Razão: Assíncrono, Type hints, auto-docs (OpenAPI/Swagger)
├─ ORM/Data: Pandas 2.x + Pydantic v2
│  └─ Razão: Processamento eficiente de CSVs, validação de schemas
├─ Export: PM4Py (XES)
│  └─ Razão: Padrão de process mining, compatível com ProM/Disco
├─ Config: PyYAML
│  └─ Razão: Regras em YAML (extensível sem código)
├─ Testing: pytest
│  └─ Razão: Standard Python, fixtures robustas
└─ Deploy: Docker
   └─ Razão: Isolamento, cross-platform, CI/CD ready

FRONTEND STACK
├─ Framework: React 18 + TypeScript
│  └─ Razão: Type safety, componentes reutilizáveis, grande comunidade
├─ Build: Vite
│  └─ Razão: Fast dev server, otimized build, zero-config setup
├─ HTTP: Fetch API + TanStack Query
│  └─ Razão: Nativa no browser, polling para status
├─ Styling: Tailwind CSS
│  └─ Razão: Utility-first, rápido de desenvolver, responsive by default
├─ Upload: react-dropzone
│  └─ Razão: Drag & drop, zero-configuration
└─ Deploy: Docker
   └─ Razão: Mesmo container estratégia que backend

INFRASTRUCTURE
├─ Docker Compose (local development)
├─ GitHub Actions (CI/CD - futuro)
├─ Cloud (Heroku/AWS/GCP - futuro)
└─ Database (PostgreSQL - futuro, MVP usa file system)

RATIONALE: MVP minimalista focado em:
  1. Auto-detection (core differentiator)
  2. 3-click UX (zero configuration)
  3. Cross-platform (Docker)
  4. Open source (permissive license)
  5. Extensível (YAML rules, plugin architecture)
```

---

## 🔟 Validação da Arquitetura

### ✅ Critérios Atendidos:

| Critério | Status | Evidência |
|----------|--------|-----------|
| **Auto-Detection** | ✅ | 3 detectores (CSV, columns, timestamp) |
| **3-Click UX** | ✅ | Upload → Process → Download |
| **Multi-Formato Export** | ✅ | CSV + XES, 2 versões cada |
| **Bloom Taxonomy** | ✅ | 13 regras em YAML |
| **Cross-Platform** | ✅ | Docker para backend + frontend |
| **Type-Safe** | ✅ | Pydantic + TypeScript |
| **Testable** | ✅ | Unit + Integration tests planificados |
| **Extensível** | ✅ | YAML rules, plugin-ready |
| **Performance** | ✅ | <25s para 5k eventos |
| **Scalable** | ✅ | Async FastAPI, can add queue system |

### ⚠️ Trade-offs:

| Decisão | Trade-off |
|---------|-----------|
| File system vs Database | ✅ Simples (MVP), ❌ Não persistente |
| In-memory jobs vs Queue | ✅ Rápido (MVP), ❌ Sem async jobs |
| Hard-coded defaults vs Config | ✅ ZERO config (UX!), ❌ Inflexível |
| 13 rules vs ML | ✅ Determinístico, ❌ Não adapta |
| Single page vs Routing | ✅ Simples (MVP), ❌ Sem navegação |

---

## 📋 Checklist de Validação

```
ARQUITETURA VALIDADA? ✅

□ Requisitos funcionais cobertos?     ✅ Sim
□ Requisitos não-funcionais?           ✅ Sim
□ Stack tecnológico apropriado?        ✅ Sim
□ Design patterns aplicáveis?          ✅ Sim
□ Dependências entre stories?          ✅ Mapeadas
□ Estrutura de pastas clara?           ✅ Definida
□ Data models completos?               ✅ Especificados
□ Pipeline bem documentado?            ✅ Diagramado
□ Pronto para implementação?           ✅ SIM! ✅
```

---

**Gerado por**: Orion (AIOS Master)
**Data**: 2026-01-28
**Status**: ✅ Arquitetura Validada e Pronta para Implementação
