# 🎓 MoodleLogSmart

> Transforme logs do Moodle em análises de aprendizagem semânticas usando a Taxonomia de Bloom

[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React 18+](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Status: MVP Completo](https://img.shields.io/badge/Status-MVP%20Completo-brightgreen.svg)](https://github.com/vertumno/moodle-log-smart)

## 📋 Visão Geral

MoodleLogSmart é uma ferramenta open-source que converte logs brutos do Moodle em análises semânticas avançadas usando a Taxonomia de Bloom. Automatiza a detecção de formato, mapeamento de colunas, limpeza de dados e enriquecimento semântico com zero configuração necessária.

### Aplicação em Produção

- **Frontend**: https://moodle-log-smart.vercel.app
- **Backend API**: https://moodle-log-smart-backend.onrender.com
- **Repositório**: https://github.com/vertumno/moodle-log-smart

---

## ⚡ Quick Start (3 passos)

### 1. Pré-requisitos

```bash
# Opção A: Com Docker (recomendado)
- Docker >= 20.10
- Docker Compose >= 2.0

# Opção B: Desenvolvimento local
- Python 3.11+
- Node.js 18+
- npm ou yarn
```

### 2. Clonar e Configurar

```bash
# Clone o repositório
git clone https://github.com/vertumno/moodle-log-smart
cd moodle-log-smart

# Copie o arquivo de configuração
cp .env.example .env

# Gere uma chave API segura
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Adicione a chave gerada em: .env → API_KEYS
```

### 3. Iniciar a Aplicação

#### Com Docker (Recomendado)
```bash
docker-compose up
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
```

#### Desenvolvimento Local

**Backend:**
```bash
cd backend
poetry install
poetry run uvicorn src.moodlelogsmart.main:app --reload --host 0.0.0.0
```

**Frontend (novo terminal):**
```bash
cd frontend
npm install
npm run dev
```

---

## ✨ Principais Funcionalidades

### 1. **Auto-Detecção Inteligente**
- ✅ Detecta automaticamente codificação (UTF-8, ISO-8859-1, etc.)
- ✅ Identifica delimitador (vírgula, ponto-e-vírgula, tab)
- ✅ Mapeia colunas Moodle com fuzzy matching
- ✅ Reconhece formato de timestamp (DD/MM/YYYY, YYYY-MM-DD, Unix, etc.)

### 2. **Limpeza e Normalização**
- ✅ Filtra eventos por papel (apenas estudantes)
- ✅ Remove eventos inválidos ou duplicados
- ✅ Normaliza timestamps para ISO 8601
- ✅ Valida consistência de dados

### 3. **Enriquecimento Semântico**
- ✅ Classifica eventos com Taxonomia de Bloom (6 níveis)
- ✅ 13 regras semânticas customizáveis
- ✅ Suporte para PT-BR e EN
- ✅ Preserve contexto pedagógico

### 4. **Exportação Multi-Formato**
- ✅ CSV enriquecido com classificações
- ✅ XES (ProM/Disco compatible) para Process Mining
- ✅ ZIP contendo todos os formatos
- ✅ Metadados de processamento

### 5. **Segurança Produção-Ready**
- ✅ Autenticação via API Key (X-API-Key header)
- ✅ Validação de UUID (prevenção path traversal)
- ✅ Prevenção de CSV injection
- ✅ CORS configurado corretamente
- ✅ Security headers (CSP, X-Frame-Options, HSTS)
- ✅ Timeout de jobs (10 minutos)
- ✅ Limpeza automática de arquivos (TTL-based)

### 6. **Interface Minimalista**
- ✅ Drag & drop para upload
- ✅ Barra de progresso em tempo real
- ✅ Auto-refresh de status
- ✅ Download automático ao concluir
- ✅ Responsiva e touch-friendly

---

## 🏗️ Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────────────────┐
│                     MOODLE LOG PROCESSING                   │
└─────────────────────────────────────────────────────────────┘

  ENTRADA                  PROCESSAMENTO                 SAÍDA
   (CSV)              (Backend FastAPI)            (ZIP contendo)
    │                      │                           │
    ├─→ Auto-Detecção ────→├─→ Limpeza             ├─→ CSV Enriquecido
    │   • Encoding         │   • Filtros           │
    │   • Delimiter        │   • Validação         ├─→ CSV Bloom Only
    │   • Colunas          │                       │
    │   • Timestamps    ┌──┴──→ Enriquecimento    ├─→ XES (ProM)
    │                  │       • Bloom Rules      │
    └──────────────────┘       • Semântica        └─→ XES Bloom Only
                           │
                           └──→ Export
                               • ZIP

TEMPO ESTIMADO: 5000 eventos = < 2 minutos
```

---

## 📦 Estrutura do Projeto

```
moodle-log-smart/
│
├── frontend/                    # React + Vite
│   ├── src/
│   │   ├── components/         # UI Components
│   │   ├── hooks/              # Custom React Hooks
│   │   ├── services/           # API Client
│   │   └── styles/             # Tailwind CSS
│   ├── package.json
│   └── Dockerfile
│
├── backend/                     # Python FastAPI
│   ├── src/moodlelogsmart/
│   │   ├── api/                # FastAPI Endpoints
│   │   │   ├── main.py        # App initialization
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── models.py      # Pydantic models
│   │   │   ├── validators.py  # Input validation
│   │   │   └── job_manager.py # Job orchestration
│   │   │
│   │   ├── core/               # Business Logic
│   │   │   ├── auto_detect/   # Auto-detection engine
│   │   │   ├── clean/         # Data cleaning
│   │   │   ├── rules/         # Bloom classification
│   │   │   └── export/        # Multi-format export
│   │   │
│   │   └── domain/             # Data models
│   │
│   ├── tests/                  # Test suite (>95% coverage)
│   ├── pyproject.toml
│   └── Dockerfile
│
├── docs/                        # Documentation
│   ├── deployment/             # Deployment guides
│   ├── architecture/           # System design
│   ├── stories/                # User stories & specs
│   └── qa/                     # QA reports
│
├── scripts/                     # Utility scripts
├── docker-compose.yml          # Local development
├── docker-compose.prod.yml     # Production config
└── README.md
```

---

## 🚀 Deployment

### Vercel (Frontend)

```bash
# Deployment automático via GitHub
# Branch: main → Vercel staging
# Tag: v*.*.* → Vercel production
```

**Link**: https://moodle-log-smart.vercel.app

### Render (Backend)

```bash
# Deployment automático via GitHub
# Branch: main → Render staging
# Tag: v*.*.* → Render production
```

**Link**: https://moodle-log-smart-backend.onrender.com

**Variáveis de Ambiente Necessárias:**
```
PYTHON_VERSION=3.11
API_KEYS=sua-chave-api-secreta
UPLOAD_DIR=/tmp/uploads
JOBS_DIR=/tmp/jobs
MAX_FILE_SIZE_MB=50
BLOOM_RULES_ENABLED=true
```

Veja [DEPLOYMENT.md](./DEPLOYMENT.md) para instruções completas de deployment.

---

## 📚 Documentação Completa

### Para Desenvolvedores
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Guia de contribuição e setup local
- **[API.md](./docs/API.md)** - Documentação completa dos endpoints
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Diagrama e design do sistema

### Para Operações
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deploy em Vercel + Render
- **[docs/deployment/](./docs/deployment/)** - Guias operacionais
  - [DEPLOYMENT-GUIDE.md](./docs/deployment/DEPLOYMENT-GUIDE.md) - Deployment local/servidor
  - [PRODUCTION-CHECKLIST.md](./docs/deployment/PRODUCTION-CHECKLIST.md) - Pré-launch
  - [SECURITY.md](./docs/deployment/SECURITY.md) - Segurança
  - [OPERATIONS-GUIDE.md](./docs/deployment/OPERATIONS-GUIDE.md) - Operações diárias

### Para Produto
- **[PRD](./docs/PRD-MoodleLogSmart.md)** - Product Requirements Document
- **[Stories](./docs/stories/)** - User stories e especificações
- **[PROJECT-STATUS.md](./PROJECT-STATUS.md)** - Dashboard de progresso

---

## 🧪 Testes

### Executar Todos os Testes

```bash
# Backend
cd backend
poetry run pytest tests/ -v --cov

# Frontend
cd frontend
npm test

# E2E Integration
./scripts/test-e2e.sh
```

### Cobertura de Testes

- **Backend**: >95% (21 testes abrangentes)
- **Frontend**: >85% (componentes UI + hooks)
- **E2E**: Fluxo completo upload → processing → download

---

## 🔒 Segurança

O projeto passou por revisão completa de segurança (QA Approved - 2026-01-29).

### Recursos de Segurança Implementados

```
✅ API Key Authentication (X-API-Key header)
✅ Job Ownership Enforcement (usuários só acessam seus jobs)
✅ UUID Validation (prevenção de path traversal)
✅ CSV Injection Prevention (detecção de caracteres fórmula)
✅ Security Headers (CSP, X-Frame-Options, HSTS)
✅ CORS Properly Configured (sem wildcard)
✅ Rate Limiting Support (pronto para middleware)
✅ Job Timeout Protection (10 minutos)
✅ Automatic File Cleanup (TTL-based)
✅ Non-root Container Execution
✅ Input Validation (todos os endpoints)
```

**Score de Segurança**: 98/100

Veja [docs/deployment/SECURITY.md](./docs/deployment/SECURITY.md) para detalhes.

---

## 📊 Métricas do Projeto

| Métrica | Valor |
|---------|-------|
| **Status** | ✅ MVP Completo & Production Ready |
| **Total de Stories** | 20 (100% concluído) |
| **Criteria de Aceitação** | 66 (100% verificado) |
| **Linhas de Código** | ~9,000 |
| **Documentação** | ~100KB |
| **Cobertura de Testes** | >95% |
| **Score de Segurança** | 98/100 |
| **Tempo de Processamento** | < 2 min (5000 eventos) |

---

## 🎯 Status de Desenvolvimento

### Epics Completos

| Epic | Stories | Status | Data |
|------|---------|--------|------|
| **Epic 1** - Backend Core | 7/7 | ✅ Completo | 2026-01-25 |
| **Epic 2** - API Layer | 7/7 | ✅ QA Aprovado | 2026-01-29 |
| **Epic 3** - Frontend | 4/4 | ✅ Completo | 2026-01-28 |
| **Epic 4** - Docker & Deploy | 4/4 | ✅ QA Aprovado | 2026-01-29 |

**Progresso Geral**: ✅ **100% (20/20 stories)**

Veja [PROJECT-STATUS.md](./PROJECT-STATUS.md) para dashboard detalhado.

---

## 🛠️ Stack Tecnológico

### Frontend
- **React** 18+
- **TypeScript**
- **Vite** (build tool)
- **Tailwind CSS** (styling)
- **Axios** (HTTP client)

### Backend
- **Python** 3.11+
- **FastAPI** (web framework)
- **Pydantic** (validation)
- **Poetry** (dependency management)
- **Pytest** (testing)

### DevOps
- **Docker** & Docker Compose
- **Vercel** (Frontend hosting)
- **Render** (Backend hosting)
- **GitHub Actions** (CI/CD)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Este é um projeto open-source com licença MIT.

### Passos para Contribuir

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/moodle-log-smart`
3. **Crie um branch**: `git checkout -b feature/sua-feature`
4. **Faça suas mudanças** (veja [CONTRIBUTING.md](./CONTRIBUTING.md))
5. **Teste**: `npm test` (frontend) e `poetry run pytest` (backend)
6. **Commit**: `git commit -m "feat: adicione sua feature"`
7. **Push**: `git push origin feature/sua-feature`
8. **Abra um Pull Request** no repositório original

Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para detalhes completos.

---

## 🐛 Bugs e Sugestões

Encontrou um bug? Tem uma sugestão? **Abra uma issue**!

- **Bug Report**: https://github.com/vertumno/moodle-log-smart/issues/new?template=bug_report.md
- **Feature Request**: https://github.com/vertumno/moodle-log-smart/issues/new?template=feature_request.md

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**. Veja [LICENSE](./LICENSE) para detalhes completos.

---

## 🙏 Agradecimentos

Inspirado por [Moodle2EventLog](https://github.com/luisrodriguez1/Moodle2EventLog) - trazendo capacidades open-source e cross-platform para análise de aprendizagem.

**Desenvolvido com ❤️** para educadores e pesquisadores em análise de aprendizagem.

---

## 👨‍💻 Autor

**Elton Vertumno**
- GitHub: [@vertumno](https://github.com/vertumno)
- Email: elton@example.com

---

## 📞 Suporte

- 📖 **Documentação**: [docs/](./docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/vertumno/moodle-log-smart/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/vertumno/moodle-log-smart/discussions)
- 🌐 **Aplicação**: https://moodle-log-smart.vercel.app

---

**Última Atualização**: 2026-01-30 | **Versão**: 1.0.0

**Status**: ✅ **MVP COMPLETO & PRODUCTION READY**
