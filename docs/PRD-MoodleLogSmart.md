# Product Requirements Document: MoodleLogSmart

**Version**: 1.0
**Status**: Draft
**Last Updated**: 2026-01-28
**Product Manager**: Morgan
**Document Type**: Brownfield PRD

---

## 📋 Executive Summary

### Product Vision
Criar um sistema **open source, moderno e extremamente simples** para processar logs do Moodle, transformando-os em logs enriquecidos semanticamente baseados na **Taxonomia de Bloom**, permitindo análises pedagógicas e process mining educacional.

### Problem Statement
Atualmente, o **Moodle2EventLog** (sistema existente) é:
- ❌ **Closed source** (executável .exe compilado em C#)
- ❌ **Windows-only** (não funciona em macOS/Linux)
- ❌ **Configuração complexa** (requer edição manual de JSON)
- ❌ **13 regras hard-coded** (difícil estender para novos cenários)
- ❌ **Sem interface web** (apenas desktop app)

Educadores e pesquisadores precisam de uma ferramenta **acessível, multiplataforma e sem fricção** para transformar logs brutos do Moodle em insights pedagógicos.

### Solution Overview
Sistema web de **1 página única** onde o usuário:
1. **Faz upload do CSV** (drag & drop)
2. **Clica "Processar"** (zero configuração manual)
3. **Baixa ZIP de resultados** (CSV + XES enriquecidos)

**Diferencial Principal**: **Auto-detection** completa (formato CSV, timestamp, colunas) + **defaults inteligentes** = experiência de 3 cliques.

### Success Metrics
- **UX**: Usuário processa log em **< 3 cliques** (upload → processar → download)
- **Performance**: Processar log de 5000 eventos em **< 2 minutos**
- **Compatibilidade**: Outputs equivalentes ao Moodle2EventLog original
- **Adoption**: **100+ downloads** no primeiro mês pós-lançamento
- **Quality**: **Zero bugs críticos** reportados no MVP

---

## 🎯 Product Goals & Objectives

### Primary Goals (Must-Have)
1. **Substituir sistema original** com funcionalidade equivalente
2. **Eliminar fricção de configuração** (auto-detection completa)
3. **Interface ultra-simples** (1 página, máximo 3 cliques)
4. **Cross-platform** (Windows, macOS, Linux via Docker)
5. **Open source** (MIT/Apache 2.0 license)

### Secondary Goals (Should-Have)
6. **Extensibilidade** via regras YAML customizáveis
7. **Documentação clara** (README de 3 passos)
8. **Deploy simplificado** (`docker-compose up`)

### Stretch Goals (Could-Have)
9. Visualizações interativas de atividades pedagógicas
10. Machine Learning para classificação automática
11. API REST para integração com outros sistemas

---

## 👥 Target Users

### Primary Persona: Professor/Pesquisador Educacional
**Name**: Dr. Ana Silva
**Role**: Professora universitária
**Tech Savvy**: Médio (usa Moodle, Excel, não sabe programar)
**Pain Points**:
- Precisa analisar logs do Moodle para pesquisa educacional
- Sistema atual (Moodle2EventLog.exe) só roda em Windows
- Não entende configuração JSON (sempre usa defaults)
- Quer resultados rápidos sem configuração complexa

**Jobs-to-be-Done**:
- Exportar logs do Moodle
- Processar logs para obter atividades classificadas (Bloom)
- Gerar arquivos XES para process mining (ProM, Disco)
- Analisar padrões de aprendizagem dos alunos

**Success Criteria**:
- ✅ Consegue processar logs sem ajuda técnica
- ✅ Recebe resultados em < 5 minutos
- ✅ Não precisa ler manual de 20 páginas

### Secondary Persona: Administrador TI Educacional
**Name**: Carlos Mendes
**Role**: Administrador de sistemas (universidade)
**Tech Savvy**: Alto (sabe Docker, Linux, DevOps)
**Pain Points**:
- Precisa deployar ferramentas para professores
- Sistema atual é executável Windows (dificulta deploy em servidores)
- Quer solução containerizada e automatizada

**Jobs-to-be-Done**:
- Deployar sistema para múltiplos usuários
- Garantir disponibilidade e performance
- Manter sistema atualizado

**Success Criteria**:
- ✅ Deploy com 1 comando (`docker-compose up`)
- ✅ Sistema roda em Linux server
- ✅ Fácil de atualizar (pull Docker image)

---

## 🏗️ System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React)                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Single Page App (1 página única)            │  │
│  │  - UploadZone (drag & drop)                  │  │
│  │  - ProgressBar (polling status)              │  │
│  │  - DownloadButton (ZIP results)              │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │ REST API (3 endpoints)
                   ↓
┌─────────────────────────────────────────────────────┐
│              BACKEND (Python/FastAPI)               │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Layer                                    │  │
│  │  - POST /api/upload                          │  │
│  │  - GET /api/status/{job_id}                  │  │
│  │  - GET /api/download/{job_id}                │  │
│  └──────────────────┬───────────────────────────┘  │
│                     ↓                               │
│  ┌──────────────────────────────────────────────┐  │
│  │  AUTO-DETECTION MODULE (NOVO!)               │  │
│  │  - CSVDetector (encoding, delimiter)         │  │
│  │  - ColumnMapper (mapeia colunas Moodle)      │  │
│  │  - TimestampDetector (formato de data)       │  │
│  └──────────────────┬───────────────────────────┘  │
│                     ↓                               │
│  ┌──────────────────────────────────────────────┐  │
│  │  PROCESSING PIPELINE                         │  │
│  │  1. Cleaning (filtros automáticos)           │  │
│  │  2. Enrichment (13 regras Bloom)             │  │
│  │  3. Export (CSV + XES + ZIP)                 │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | React 18 + JavaScript | Simples, rápido, sem overhead de TypeScript no MVP |
| **Backend** | Python 3.11 + FastAPI | Compatível com pandas/numpy, docs automáticas |
| **Data Processing** | Pandas + NumPy | Industry standard para CSV processing |
| **Process Mining** | PM4Py | Geração de XES para ProM/Disco |
| **Deployment** | Docker + Docker Compose | Deploy com 1 comando, cross-platform |

---

## ✨ Core Features & Requirements

### Feature 1: Auto-Detection de Formato CSV

**Priority**: Must-Have (P0)
**User Story**: Como usuário, quero fazer upload de qualquer CSV do Moodle sem configurar formato, para economizar tempo.

**Requirements**:
- **FR-1.1**: Sistema detecta encoding automaticamente (UTF-8, Latin-1, CP1252)
- **FR-1.2**: Sistema detecta delimiter automaticamente (, ; \t |)
- **FR-1.3**: Sistema mapeia colunas Moodle automaticamente (fuzzy matching)
- **FR-1.4**: Sistema detecta formato de timestamp automaticamente (10+ formatos)
- **FR-1.5**: Sistema exibe erro claro se CSV for inválido

**Acceptance Criteria**:
- ✅ Processa CSV com encoding UTF-8
- ✅ Processa CSV com delimiter ","
- ✅ Processa CSV com delimiter ";"
- ✅ Detecta colunas: "Time", "Event name", "Component", "User full name"
- ✅ Detecta timestamps no formato: "%d/%m/%y, %H:%M:%S"
- ✅ Detecta timestamps no formato: "%Y-%m-%d %H:%M:%S"

**Technical Approach**:
- Módulo `CSVDetector` usando chardet para encoding
- Módulo `ColumnMapper` com dicionário de aliases conhecidos
- Módulo `TimestampDetector` testando formatos comuns

**Dependencies**: Pandas, chardet

---

### Feature 2: Interface de 1 Página (Zero Configuração)

**Priority**: Must-Have (P0)
**User Story**: Como usuário não-técnico, quero interface simples onde arrasto CSV e baixo resultados, sem configurar nada.

**Requirements**:
- **FR-2.1**: Zona de upload com drag & drop
- **FR-2.2**: Validação de arquivo (apenas .csv aceito)
- **FR-2.3**: Progress bar mostrando % de progresso
- **FR-2.4**: Botão de download aparece quando processamento completa
- **FR-2.5**: Mensagem de erro clara se processamento falhar

**Acceptance Criteria**:
- ✅ Usuário arrasta CSV para zona de upload
- ✅ Sistema valida que arquivo é .csv (rejeita .xlsx, .txt)
- ✅ Progress bar atualiza a cada 5 segundos
- ✅ Download button baixa ZIP com 4 arquivos
- ✅ Erro mostra mensagem compreensível (não stack trace)

**UX Flow**:
```
1. Página carrega → Exibe zona de upload
2. Usuário arrasta CSV → Arquivo valida, envia para backend
3. Backend processa → Progress bar mostra % (0→100%)
4. Processamento completa → Download button aparece
5. Usuário clica download → ZIP baixa automaticamente
```

**Technical Approach**:
- React component `UploadZone` usando react-dropzone
- Polling a cada 5s para atualizar progress bar
- Backend retorna progress via endpoint `/api/status/{job_id}`

**Dependencies**: React, react-dropzone, fetch API

---

### Feature 3: Enriquecimento Semântico (Bloom's Taxonomy)

**Priority**: Must-Have (P0)
**User Story**: Como pesquisador educacional, quero logs enriquecidos com atividades classificadas segundo Bloom, para analisar níveis cognitivos dos alunos.

**Requirements**:
- **FR-3.1**: Mapear eventos Moodle → Atividades Semânticas
- **FR-3.2**: Classificar atividades em níveis de Bloom (Remember, Understand, Apply, Analyze, Evaluate, Create)
- **FR-3.3**: Diferenciar ações Passivas (_P) vs Ativas (_A)
- **FR-3.4**: Implementar 13 regras do sistema original
- **FR-3.5**: Regras extensíveis via YAML (para usuários avançados)

**Bloom Taxonomy Mapping**:

| Atividade Semântica | Nível Bloom | Descrição | Exemplo |
|---------------------|-------------|-----------|---------|
| **Study_P** | Remember | Visualizar materiais (passivo) | Download de slides |
| **Study_A** | Understand | Completar leitura (ativo) | Marcar leitura como concluída |
| **Exercise_P** | Apply | Ver exercício (passivo) | Visualizar worksheet |
| **Exercise_A** | Apply | Resolver exercício (ativo) | Submeter assignment |
| **Assess_P** | Evaluate | Ver quiz (passivo) | Visualizar quiz |
| **Assess_A** | Evaluate | Completar quiz (ativo) | Submeter respostas |
| **Synthesize** | Create | Criar conteúdo novo | Submeter projeto |
| **View** | N/A | Navegação geral | Visualizar página |
| **Feedback** | N/A | Receber feedback | Ver nota |
| **Interact** | N/A | Interação social | Post em fórum |
| **Others** | N/A | Não categorizado | Eventos diversos |

**Acceptance Criteria**:
- ✅ "Course module viewed" + component="File" → Study_P
- ✅ "Submission created" + component="Assignment" → Exercise_A
- ✅ "Attempt submitted" + component="Quiz" → Assess_A
- ✅ "Discussion created" + component="Forum" → Interact
- ✅ Outputs incluem coluna `activity_type` e `bloom_level`

**Technical Approach**:
- Rule Engine lê regras de `bloom_taxonomy.yaml`
- Cada regra tem conditions (field, operator, value) e action (activity_type, bloom_level)
- Regras executam em ordem de prioridade
- Fallback: activity_type = "Others" se nenhuma regra match

**Dependencies**: PyYAML, Rule Engine customizado

---

### Feature 4: Export Multi-Formato

**Priority**: Must-Have (P0)
**User Story**: Como usuário, quero baixar resultados em múltiplos formatos (CSV + XES), para usar em diferentes ferramentas de análise.

**Requirements**:
- **FR-4.1**: Exportar `enriched_log.csv` (todas as atividades)
- **FR-4.2**: Exportar `enriched_log_bloom_only.csv` (apenas pedagógicas)
- **FR-4.3**: Exportar `enriched_log.xes` (process mining)
- **FR-4.4**: Exportar `enriched_log_bloom_only.xes`
- **FR-4.5**: Empacotar tudo em ZIP com timestamp no nome

**XES Format Specification**:
```xml
<log>
  <trace>
    <string key="concept:name" value="UserID_123"/>
    <event>
      <string key="concept:name" value="Study_A"/>
      <string key="lifecycle:transition" value="complete"/>
      <date key="time:timestamp" value="2024-01-15T10:30:45"/>
      <string key="org:resource" value="File"/>
    </event>
  </trace>
</log>
```

**Acceptance Criteria**:
- ✅ ZIP contém 4 arquivos
- ✅ CSV tem colunas: time, user_full_name, event_name, activity_type, bloom_level
- ✅ XES é válido (pode abrir em ProM/Disco)
- ✅ bloom_only NÃO contém: View, Feedback, Interact, Others
- ✅ Nome do ZIP: `results_YYYYMMDD_HHMMSS.zip`

**Technical Approach**:
- CSV Exporter usa Pandas `.to_csv()`
- XES Exporter usa PM4Py library
- ZIP Packager usa Python zipfile module

**Dependencies**: Pandas, PM4Py, zipfile

---

### Feature 5: Configuração Default (Zero Setup)

**Priority**: Must-Have (P0)
**User Story**: Como usuário não-técnico, quero que sistema use configuração padrão inteligente, sem precisar editar YAML/JSON.

**Requirements**:
- **FR-5.1**: studentRoleID = "5" (padrão Moodle)
- **FR-5.2**: Filtrar eventos não-estudantis (lista default)
- **FR-5.3**: Rule set = "default" (bloom_taxonomy.yaml)
- **FR-5.4**: Exports = ["csv", "xes"] (ambos sempre)
- **FR-5.5**: Sempre gerar versão bloom-only

**Default Configuration**:
```python
DEFAULT_CONFIG = {
    "filter": {
        "student_role_id": "5",
        "non_student_events": [
            "Course section deleted",
            "Course backup created",
            "Course updated"
        ]
    },
    "enrichment": {
        "rule_set": "default",
        "confidence_threshold": 0.7
    },
    "export": {
        "formats": ["csv", "xes"],
        "include_bloom_only": True,
        "package_as_zip": True
    }
}
```

**Acceptance Criteria**:
- ✅ Usuário NÃO precisa configurar nada
- ✅ Sistema usa defaults automáticos
- ✅ Usuário avançado PODE customizar via fork do repo (editar YAML)

---

## 📊 Non-Functional Requirements

### Performance
- **NFR-1**: Processar log de 1000 eventos em < 30 segundos
- **NFR-2**: Processar log de 5000 eventos em < 2 minutos
- **NFR-3**: Upload de arquivos até 50MB
- **NFR-4**: Response time da API < 200ms (exceto processamento)

### Reliability
- **NFR-5**: Sistema recupera de erros sem perda de dados
- **NFR-6**: Mensagens de erro são compreensíveis (não stack traces)
- **NFR-7**: Timeout de processamento = 10 minutos

### Usability
- **NFR-8**: Interface funciona em Chrome, Firefox, Safari, Edge
- **NFR-9**: Interface é responsiva (funciona em tablet)
- **NFR-10**: Usuário completa fluxo em < 3 cliques
- **NFR-11**: README tem quick start de 3 linhas

### Scalability
- **NFR-12**: Sistema processa 1 job por vez (MVP)
- **NFR-13**: Backend pode escalar horizontalmente (fase futura)

### Security
- **NFR-14**: Arquivos são temporários (deletados após download)
- **NFR-15**: Sem armazenamento persistente de logs (privacy)
- **NFR-16**: CORS configurado para domínios permitidos

### Compatibility
- **NFR-17**: Docker image roda em Linux, Windows, macOS
- **NFR-18**: Outputs compatíveis com ProM, Disco, Celonis
- **NFR-19**: CSV compatível com Excel, Google Sheets

---

## 🚧 Out of Scope (MVP)

### Explicitly NOT Included in MVP
- ❌ Análise estatística avançada (gráficos, distribuições)
- ❌ Machine Learning classification
- ❌ Multi-tenancy / user management
- ❌ Processamento assíncrono (Celery + Redis)
- ❌ WebSocket para real-time updates
- ❌ PostgreSQL persistence
- ❌ Visualizações interativas (Plotly)
- ❌ Configuração manual via UI (sempre usa defaults)
- ❌ Batch processing de múltiplos arquivos
- ❌ Autenticação / autorização

### Future Roadmap (Post-MVP)
**Fase 2** (após MVP):
- Visualizações interativas de learning paths
- Configuração opcional via UI
- Batch processing

**Fase 3**:
- Machine Learning classifier
- Multi-tenancy
- API REST avançada

**Fase 4**:
- Cloud deployment
- Monitoramento (Prometheus + Grafana)
- CI/CD completo

---

## 📅 Timeline & Milestones

### Sprint 1: Backend Core + Auto-Detection (1 semana)
**Goal**: Pipeline funcional (CSV → ZIP)

**Deliverables**:
- ✅ Auto-detection modules (CSV, columns, timestamp)
- ✅ Data cleaning com defaults
- ✅ Rule engine (13 regras)
- ✅ CSV + XES exporters
- ✅ ZIP packager

**Exit Criteria**:
- Pipeline processa CSV sample e gera ZIP válido
- Tests unitários >50% coverage

---

### Sprint 2: API Layer (3-4 dias)
**Goal**: API REST minimalista

**Deliverables**:
- ✅ FastAPI app
- ✅ 3 endpoints (upload, status, download)
- ✅ Job management em memória
- ✅ Error handling básico

**Exit Criteria**:
- API aceita upload, processa, retorna ZIP
- OpenAPI docs geradas automaticamente

---

### Sprint 3: Frontend Minimalista (3-4 dias)
**Goal**: Interface de 1 página

**Deliverables**:
- ✅ React app (1 arquivo App.jsx)
- ✅ UploadZone component
- ✅ ProgressBar com polling
- ✅ DownloadButton

**Exit Criteria**:
- Usuário completa fluxo: upload → processar → download
- Interface funciona em Chrome/Firefox

---

### Sprint 4: Docker + Docs (2-3 dias)
**Goal**: Deploy com 1 comando

**Deliverables**:
- ✅ Dockerfiles (backend + frontend)
- ✅ docker-compose.yml
- ✅ README com quick start
- ✅ Integration testing

**Exit Criteria**:
- `docker-compose up` inicia sistema funcional
- README tem instruções de 3 passos

---

### MVP Launch (Total: 2-3 semanas)
**Target**: Sistema funcional end-to-end

**Success Metrics**:
- ✅ UX de 3 cliques funciona
- ✅ Processa logs equivalentes ao original
- ✅ Deploy com 1 comando
- ✅ README claro e simples

---

## 🎯 Success Criteria & KPIs

### MVP Success Criteria (Must Achieve)
- ✅ **Functional**: Processa logs do Moodle corretamente
- ✅ **UX**: Usuário completa fluxo em < 3 cliques
- ✅ **Performance**: Processa 5000 eventos em < 2 minutos
- ✅ **Compatibility**: Outputs equivalentes ao Moodle2EventLog
- ✅ **Deploy**: `docker-compose up` funciona first try

### Post-Launch KPIs (Track After Release)
- **Adoption**: 100+ downloads no primeiro mês
- **Retention**: 50% dos usuários processam >1 log
- **Quality**: Zero bugs críticos reportados
- **Support**: < 5% dos usuários precisam de ajuda
- **Satisfaction**: NPS >30

### Failure Criteria (Red Flags)
- ❌ Usuário não consegue processar log sem ajuda
- ❌ Processamento leva > 5 minutos para log típico
- ❌ Outputs não são compatíveis com ProM/Disco
- ❌ Docker deploy falha em Windows/macOS/Linux
- ❌ >10% dos usuários reportam bugs críticos

---

## 🔍 Assumptions & Dependencies

### Assumptions
1. **User Assumption**: Usuários têm acesso a logs CSV do Moodle
2. **Technical Assumption**: Logs seguem formato padrão Moodle 3.x/4.x
3. **Infrastructure Assumption**: Usuários podem rodar Docker
4. **Data Assumption**: Logs contém colunas mínimas (Time, Event name, Component)
5. **Adoption Assumption**: Educadores preferem ferramenta open source vs closed source

### Dependencies
**External Dependencies**:
- Moodle platform (source dos logs)
- Docker ecosystem (deploy)
- PM4Py library (XES export)
- Pandas library (data processing)

**Internal Dependencies**:
- Templates de regras YAML
- Sample data para testing
- Documentation (README)

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Formato CSV do Moodle muda | Alto | Baixo | Auto-detection robusta com fallbacks |
| Performance insuficiente | Médio | Baixo | Otimizar pandas, usar chunking |
| Docker não roda em Windows | Alto | Baixo | Testar em Windows WSL2 |
| Outputs incompatíveis com ProM | Alto | Baixo | Validar XES com PM4Py test suite |
| Usuários não entendem interface | Médio | Baixo | UX testing com 5 usuários reais |

---

## 🤝 Stakeholders & Communication Plan

### Key Stakeholders

**Primary Stakeholder**: Dr. Ana Silva (Professora/Pesquisadora)
- **Interest**: Ferramenta funcional para pesquisa educacional
- **Communication**: Email semanal com progresso
- **Decision Rights**: Aprovação de UX e features

**Secondary Stakeholder**: Carlos Mendes (Admin TI)
- **Interest**: Deploy fácil e manutenção baixa
- **Communication**: Demo ao final de cada sprint
- **Decision Rights**: Aprovação de infra e deploy

**Tertiary Stakeholder**: Comunidade Open Source
- **Interest**: Código de qualidade, documentação clara
- **Communication**: GitHub issues e discussions
- **Decision Rights**: Contribuições via PR

### Communication Cadence
- **Daily**: Stand-up async (progress update)
- **Weekly**: Sprint review (demo funcional)
- **Bi-weekly**: Stakeholder sync (email summary)
- **Monthly**: Community update (blog post/release notes)

---

## 📚 References & Research

### Existing System Analysis
- **Moodle2EventLog**: https://gitlab.univ-lr.fr/njoudi01/moodle2eventlog
- **Publication**: CSEDU 2025 - "Moodle2EventLog: A Tool for Pedagogically-Driven Log Enrichment"
- **DOI**: 10.5220/0013327300003932

### Technical References
- **Bloom's Revised Taxonomy**: Anderson & Krathwohl (2001)
- **Process Mining**: Van der Aalst, W. (2016)
- **PM4Py Documentation**: https://pm4py.fit.fraunhofer.de/
- **Moodle Logging API**: https://docs.moodle.org/dev/Logging_API

### Competitive Analysis
**Similar Tools**:
- Moodle2EventLog (original) - Windows only, closed source
- ProM plugins - Complexos, requerem conhecimento técnico
- Custom Python scripts - Ad-hoc, sem interface

**Differentiation**:
- ✅ Open source (vs closed source)
- ✅ Web interface (vs desktop app)
- ✅ Zero configuration (vs manual setup)
- ✅ Cross-platform (vs Windows only)

---

## ✅ Approval & Sign-off

### PRD Approval Process
1. **Draft Review**: PM creates PRD → Shares with stakeholders
2. **Feedback Round**: Stakeholders provide input (1 week)
3. **Revision**: PM incorporates feedback
4. **Final Approval**: Stakeholders sign-off
5. **Handoff**: PRD goes to @architect for technical design

### Approvers

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Manager | Morgan | ✅ Approved | 2026-01-28 |
| Tech Lead / Architect | Aria | ⏳ Pending | - |
| Primary Stakeholder | Dr. Ana Silva | ⏳ Pending | - |
| Secondary Stakeholder | Carlos Mendes | ⏳ Pending | - |

---

## 📝 Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-28 | Morgan | Initial PRD creation based on detailed plan |

---

**Next Steps**:
1. ✅ PRD created and documented
2. ⏳ Review with @architect for technical feasibility
3. ⏳ Stakeholder approval round
4. ⏳ Create epics and breakdown into stories (@sm)
5. ⏳ Begin Sprint 1 implementation (@dev)

---

*Document prepared by Morgan (Product Manager)*
*"Planejando o futuro 📊"*