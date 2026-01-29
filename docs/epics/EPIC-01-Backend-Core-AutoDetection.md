# Epic 1: Backend Core + Auto-Detection

**Epic ID**: EPIC-01
**Product**: MoodleLogSmart
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 1
**Duration**: 1 semana (5 dias úteis)
**Status**: Not Started
**Epic Owner**: @dev (Development Team)

---

## 📋 Epic Overview

### Epic Goal
Implementar o **pipeline de processamento completo** (CSV → ZIP) com **auto-detection inteligente** de formato, colunas e timestamps, eliminando necessidade de configuração manual.

### Business Value
- **Elimina fricção de setup**: Usuários não precisam configurar formato CSV
- **Suporta múltiplos formatos**: Detecta automaticamente variações de Moodle
- **Base sólida**: Pipeline core funcional para sprints seguintes

### Success Criteria
- ✅ Pipeline processa CSV sample e gera ZIP válido com 4 arquivos
- ✅ Auto-detection funciona para 3+ formatos de timestamp
- ✅ Auto-detection funciona para 2+ encodings (UTF-8, Latin-1)
- ✅ 13 regras Bloom implementadas e funcionando
- ✅ Tests unitários >50% coverage

---

## 🎯 Objectives & Key Results (OKRs)

**Objective**: Criar pipeline funcional com zero configuração manual

**Key Results**:
1. **KR1**: Auto-detect CSV format com 95% de acurácia (encoding + delimiter)
2. **KR2**: Auto-detect timestamp format para 10+ variações comuns
3. **KR3**: Auto-map colunas Moodle com fuzzy matching (90% acurácia)
4. **KR4**: Processar 1000 eventos em <30 segundos
5. **KR5**: Gerar ZIP com 4 arquivos válidos (CSV + XES)

---

## 👥 User Stories

### Story 1.1: Auto-Detection de Encoding e Delimiter
**As a** usuário não-técnico
**I want** fazer upload de CSV sem saber encoding/delimiter
**So that** não preciso configurar detalhes técnicos

**Acceptance Criteria**:
- ✅ Detecta UTF-8, Latin-1, CP1252 automaticamente
- ✅ Detecta delimiters: , ; \t |
- ✅ Valida estrutura básica do CSV (header row)
- ✅ Retorna erro claro se CSV inválido

**Tasks**:
- [ ] Implementar `CSVDetector` class
- [ ] Usar chardet library para encoding
- [ ] Testar delimiters comuns com sample CSVs
- [ ] Adicionar tests unitários (5+ test cases)

**Estimate**: 1 dia
**Assigned to**: @dev

---

### Story 1.2: Auto-Mapeamento de Colunas Moodle
**As a** usuário
**I want** que sistema identifique colunas automaticamente
**So that** não preciso mapear "Time" vs "Timestamp" manualmente

**Acceptance Criteria**:
- ✅ Mapeia "Time", "Timestamp", "Date/Time" → time
- ✅ Mapeia "User full name", "Full name", "Name" → user_full_name
- ✅ Mapeia "Event name", "Event", "Action" → event_name
- ✅ Mapeia "Component", "Module" → component
- ✅ Fuzzy matching com threshold 80%

**Tasks**:
- [ ] Implementar `ColumnMapper` class
- [ ] Criar dicionário de aliases conhecidos
- [ ] Implementar fuzzy matching (fuzzywuzzy/rapidfuzz)
- [ ] Testar com 3+ variações de CSV Moodle
- [ ] Adicionar tests unitários

**Estimate**: 1 dia
**Assigned to**: @dev

---

### Story 1.3: Auto-Detection de Formato de Timestamp
**As a** usuário
**I want** que sistema detecte formato de data automaticamente
**So that** não preciso especificar "%d/%m/%y, %H:%M:%S"

**Acceptance Criteria**:
- ✅ Detecta: "%d/%m/%y, %H:%M:%S" (22/08/24, 13:43:23)
- ✅ Detecta: "%Y-%m-%d %H:%M:%S" (2024-08-22 13:43:23)
- ✅ Detecta: "%d/%m/%Y %H:%M:%S" (22/08/2024 13:43:23)
- ✅ Detecta: "%m/%d/%Y %I:%M:%S %p" (08/22/2024 01:43:23 PM)
- ✅ Fallback para pandas auto-inference se formato desconhecido

**Tasks**:
- [ ] Implementar `TimestampDetector` class
- [ ] Criar lista de 10+ formatos comuns
- [ ] Testar cada formato com sample data
- [ ] Implementar fallback logic
- [ ] Adicionar tests unitários

**Estimate**: 1 dia
**Assigned to**: @dev

---

### Story 1.4: Data Cleaning com Configuração Default
**As a** sistema
**I want** aplicar filtros automáticos baseados em defaults
**So that** apenas eventos de estudantes sejam processados

**Acceptance Criteria**:
- ✅ Filtra por studentRoleID = "5" (padrão Moodle)
- ✅ Remove eventos em `non_student_events` list
- ✅ Valida timestamps (remove inválidos)
- ✅ Normaliza tipos de dados (strings, datetimes, etc.)

**Tasks**:
- [ ] Implementar `RoleFilter` class
- [ ] Implementar `EventFilter` class
- [ ] Implementar `TimestampValidator` class
- [ ] Implementar `DataNormalizer` class
- [ ] Criar configuração default hard-coded
- [ ] Adicionar tests unitários

**Estimate**: 1 dia
**Assigned to**: @dev

---

### Story 1.5: Rule Engine + 13 Regras Bloom
**As a** pesquisador educacional
**I want** eventos classificados segundo Taxonomia de Bloom
**So that** posso analisar níveis cognitivos

**Acceptance Criteria**:
- ✅ Rule Engine lê regras de `bloom_taxonomy.yaml`
- ✅ Implementa 13 regras do Moodle2EventLog original
- ✅ Suporta operators: equals, in, contains
- ✅ Executa regras em ordem de prioridade
- ✅ Fallback para "Others" se nenhuma regra match
- ✅ Adiciona colunas: activity_type, bloom_level, is_active

**Tasks**:
- [ ] Implementar `RuleEngine` class
- [ ] Criar parser YAML → Rule objects
- [ ] Implementar condition evaluation logic
- [ ] Migrar 13 regras para `bloom_taxonomy.yaml`
- [ ] Testar cada regra individualmente
- [ ] Adicionar tests unitários (13+ test cases)

**Estimate**: 2 dias
**Assigned to**: @dev

---

### Story 1.6: Export Multi-Formato (CSV + XES)
**As a** usuário
**I want** baixar resultados em CSV e XES
**So that** posso usar em Excel e ProM/Disco

**Acceptance Criteria**:
- ✅ Exporta `enriched_log.csv` (todas atividades)
- ✅ Exporta `enriched_log_bloom_only.csv` (filtrado)
- ✅ Exporta `enriched_log.xes` (PM4Py format)
- ✅ Exporta `enriched_log_bloom_only.xes`
- ✅ XES válido (pode abrir em ProM/Disco)
- ✅ CSV tem colunas corretas (time, user, activity_type, bloom_level)

**Tasks**:
- [ ] Implementar `CSVExporter` class (Pandas)
- [ ] Implementar `XESExporter` class (PM4Py)
- [ ] Implementar filtro bloom-only
- [ ] Validar XES com PM4Py test suite
- [ ] Adicionar tests unitários

**Estimate**: 1 dia
**Assigned to**: @dev

---

### Story 1.7: ZIP Packager
**As a** usuário
**I want** baixar todos resultados em 1 arquivo ZIP
**So that** não preciso baixar 4 arquivos separados

**Acceptance Criteria**:
- ✅ Cria ZIP contendo 4 arquivos
- ✅ Nome do ZIP: `results_YYYYMMDD_HHMMSS.zip`
- ✅ ZIP pode ser extraído normalmente
- ✅ Arquivos dentro do ZIP têm nomes corretos

**Tasks**:
- [ ] Implementar `ZIPPackager` class (zipfile)
- [ ] Adicionar timestamp ao nome do arquivo
- [ ] Testar extração do ZIP
- [ ] Adicionar tests unitários

**Estimate**: 0.5 dia
**Assigned to**: @dev

---

## 🏗️ Technical Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│            BACKEND CORE (Python)                    │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  AUTO-DETECTION MODULE                        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │ │
│  │  │CSVDetector  │ │ColumnMapper │ │Timestamp│ │ │
│  │  │             │ │             │ │Detector │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────┘ │ │
│  └───────────────────┬───────────────────────────┘ │
│                      ↓                              │
│  ┌───────────────────────────────────────────────┐ │
│  │  DATA CLEANING MODULE                         │ │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────────┐ │ │
│  │  │RoleFilter│ │EventFilter│ │TimestampValid│ │ │
│  │  └──────────┘ └───────────┘ └──────────────┘ │ │
│  └───────────────────┬───────────────────────────┘ │
│                      ↓                              │
│  ┌───────────────────────────────────────────────┐ │
│  │  ENRICHMENT MODULE                            │ │
│  │  ┌──────────────┐ ┌────────────────────────┐ │ │
│  │  │  RuleEngine  │ │ bloom_taxonomy.yaml    │ │ │
│  │  │  (13 rules)  │ │ (YAML config)          │ │ │
│  │  └──────────────┘ └────────────────────────┘ │ │
│  └───────────────────┬───────────────────────────┘ │
│                      ↓                              │
│  ┌───────────────────────────────────────────────┐ │
│  │  EXPORT MODULE                                │ │
│  │  ┌───────────┐ ┌───────────┐ ┌────────────┐ │ │
│  │  │CSVExporter│ │XESExporter│ │ZIPPackager │ │ │
│  │  └───────────┘ └───────────┘ └────────────┘ │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
CSV File Upload
     ↓
CSVDetector → (encoding, delimiter, structure)
     ↓
ColumnMapper → (standardized column names)
     ↓
TimestampDetector → (datetime parsing format)
     ↓
RoleFilter → (filter students only)
     ↓
EventFilter → (remove non-student events)
     ↓
RuleEngine → (classify Bloom activities)
     ↓
CSVExporter → enriched_log.csv + bloom_only.csv
     ↓
XESExporter → enriched_log.xes + bloom_only.xes
     ↓
ZIPPackager → results_YYYYMMDD_HHMMSS.zip
```

---

## 📁 File Structure

```
backend/
├── src/moodlelogsmart/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── event.py           # RawMoodleEvent, EnrichedActivity
│   │   │   └── rule.py            # Rule entities
│   │   └── enums.py               # ActivityType, BloomLevel
│   ├── core/
│   │   ├── auto_detect/           # ⭐ NEW MODULE
│   │   │   ├── csv_detector.py
│   │   │   ├── column_mapper.py
│   │   │   └── timestamp_detector.py
│   │   ├── cleaning/
│   │   │   ├── role_filter.py
│   │   │   ├── event_filter.py
│   │   │   └── normalizer.py
│   │   ├── enrichment/
│   │   │   ├── rule_engine.py
│   │   │   └── bloom_classifier.py
│   │   └── export/
│   │       ├── csv_exporter.py
│   │       ├── xes_exporter.py
│   │       └── zip_packager.py    # ⭐ NEW
│   ├── pipeline/
│   │   ├── builder.py
│   │   └── steps/
│   │       ├── clean_step.py
│   │       ├── enrich_step.py
│   │       └── export_step.py
│   ├── config/
│   │   ├── settings.py
│   │   └── defaults.py            # ⭐ NEW (hard-coded config)
│   └── tests/
│       ├── unit/
│       └── integration/
├── rules/
│   └── default/
│       └── bloom_taxonomy.yaml    # 13 regras
├── pyproject.toml
└── README.md
```

---

## 🧪 Testing Strategy

### Unit Tests (Target: >50% coverage)
- **Auto-detection**: 15+ test cases
  - CSV encoding detection (UTF-8, Latin-1, CP1252)
  - Delimiter detection (, ; \t |)
  - Column mapping (10+ variations)
  - Timestamp detection (10+ formats)
- **Data Cleaning**: 10+ test cases
  - Role filtering
  - Event filtering
  - Timestamp validation
- **Rule Engine**: 13+ test cases
  - 1 test per regra Bloom
  - Priority ordering
  - Fallback logic
- **Export**: 5+ test cases
  - CSV structure validation
  - XES validation (PM4Py)
  - ZIP creation

### Integration Tests
- **End-to-End Pipeline**: 3+ test cases
  - Sample CSV → ZIP completo
  - Validar 4 arquivos no ZIP
  - Comparar outputs com expected

---

## 📊 Dependencies & Risks

### Technical Dependencies
- **Python 3.11+**: Core language
- **Pandas 2.x**: CSV processing
- **PM4Py**: XES generation
- **chardet**: Encoding detection
- **PyYAML**: Rule parsing
- **rapidfuzz**: Fuzzy column matching

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Auto-detection falha para formato raro | Médio | Baixo | Implementar fallback manual override |
| Performance ruim com CSV grande | Alto | Médio | Usar pandas chunking |
| XES inválido | Alto | Baixo | Validar com PM4Py test suite |
| Regras Bloom incorretas | Alto | Baixo | Comparar outputs com Moodle2EventLog |

---

## ✅ Definition of Done (DoD)

### Epic-Level DoD
- ✅ Todas as 7 user stories completadas
- ✅ Pipeline processa sample CSV → ZIP válido
- ✅ Auto-detection funciona para 3+ formatos
- ✅ 13 regras Bloom implementadas e testadas
- ✅ Tests unitários >50% coverage
- ✅ Integration test end-to-end passa
- ✅ Code review completado
- ✅ Documentation atualizada (README)

### Story-Level DoD (cada story)
- ✅ Acceptance criteria met
- ✅ Code escrito e funcional
- ✅ Tests unitários adicionados
- ✅ Code review aprovado
- ✅ Sem code smells críticos

---

## 📈 Progress Tracking

### Sprint 1 Timeline

| Day | Focus | Stories |
|-----|-------|---------|
| **Day 1** | Auto-detection setup | Story 1.1 (CSV Detector) |
| **Day 2** | Column mapping | Story 1.2 (Column Mapper) + Story 1.3 (Timestamp) |
| **Day 3** | Data cleaning | Story 1.4 (Cleaning) |
| **Day 4** | Rule engine | Story 1.5 (Bloom Rules) |
| **Day 5** | Export + ZIP | Story 1.6 (CSV/XES) + Story 1.7 (ZIP) |

### Burndown Metrics
- **Total Story Points**: 7 stories × 1 day avg = 7 story points
- **Daily Target**: Complete 1+ story per day
- **Buffer**: 0.5 day for integration testing

---

## 🎯 Success Metrics

### Quantitative Metrics
- **Velocity**: 7 stories / 5 days = 1.4 stories/day
- **Test Coverage**: >50% (target: 60%)
- **Performance**: Process 1000 events in <30s
- **Auto-detection Accuracy**: >90% for common formats

### Qualitative Metrics
- Code is readable and maintainable
- Tests are comprehensive and meaningful
- Documentation is clear
- Team is confident in implementation

---

## 🚀 Next Steps After Epic Completion

1. **Demo to stakeholders** (Product Manager review)
2. **Handoff to Sprint 2** (API Layer development)
3. **Document learnings** (retro notes)
4. **Update architecture docs** if needed

---

**Epic Owner**: @dev
**Reviewer**: @architect (Aria)
**Approver**: @pm (Morgan)

*Created by Morgan (Product Manager)*
*Last Updated: 2026-01-28*