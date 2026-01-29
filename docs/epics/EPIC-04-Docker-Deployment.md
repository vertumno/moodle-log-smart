# Epic 4: Docker + Deployment

**Epic ID**: EPIC-04
**Product**: MoodleLogSmart
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 4
**Duration**: 2-3 dias
**Status**: Not Started
**Epic Owner**: @devops
**Dependencies**: EPIC-01, EPIC-02, EPIC-03

---

## 📋 Epic Overview

### Epic Goal
Criar **deploy com 1 comando** (`docker-compose up`) que funciona em Windows, macOS e Linux.

### Business Value
- **Instalação trivial**: Qualquer usuário consegue rodar
- **Cross-platform**: Funciona em qualquer OS com Docker
- **Reprodutível**: Ambiente idêntico em todos os lugares
- **Produção-ready**: Base para deploy em servidor

### Success Criteria
- ✅ `docker-compose up` inicia sistema funcional
- ✅ Acessa localhost:3000 e funciona
- ✅ Funciona em Windows, macOS, Linux
- ✅ README tem quick start de 3 linhas
- ✅ Documentação clara e simples

---

## 👥 User Stories

### Story 4.1: Dockerfile Backend
**As a** usuário
**I want** rodar backend em container
**So that** não preciso instalar Python/dependências

**Acceptance Criteria**:
- ✅ Dockerfile multi-stage (build + runtime)
- ✅ Imagem otimizada (<500MB)
- ✅ Instala dependências via Poetry
- ✅ Expõe porta 8000
- ✅ Health check endpoint

**Tasks**:
- [ ] Criar Dockerfile (backend)
- [ ] Multi-stage build
- [ ] Copy apenas arquivos necessários
- [ ] CMD para iniciar FastAPI
- [ ] Testar build local

**Estimate**: 0.5 dia

---

### Story 4.2: Dockerfile Frontend
**As a** usuário
**I want** rodar frontend em container
**So that** não preciso instalar Node/npm

**Acceptance Criteria**:
- ✅ Dockerfile multi-stage (build + nginx)
- ✅ Build React app (Vite)
- ✅ Serve via nginx
- ✅ Imagem otimizada (<100MB)
- ✅ Expõe porta 80

**Tasks**:
- [ ] Criar Dockerfile (frontend)
- [ ] Build stage (Vite build)
- [ ] Runtime stage (nginx)
- [ ] nginx.conf customizado
- [ ] Testar build local

**Estimate**: 0.5 dia

---

### Story 4.3: Docker Compose
**As a** usuário
**I want** iniciar sistema completo com 1 comando
**So that** setup seja trivial

**Acceptance Criteria**:
- ✅ docker-compose.yml orquestra backend + frontend
- ✅ Network configurado corretamente
- ✅ Volumes para persistência temporária
- ✅ Environment variables
- ✅ `docker-compose up` funciona first try

**Tasks**:
- [ ] Criar docker-compose.yml
- [ ] Configurar services (backend, frontend)
- [ ] Configurar network
- [ ] Configurar volumes
- [ ] Testar em 3 OS (Windows, macOS, Linux)

**Estimate**: 1 dia

---

### Story 4.4: Documentation
**As a** usuário
**I want** README com instruções claras
**So that** consiga rodar sem ajuda

**Acceptance Criteria**:
- ✅ README tem quick start (3 linhas)
- ✅ Pré-requisitos listados (Docker)
- ✅ Troubleshooting section
- ✅ Screenshots da interface
- ✅ Links para docs adicionais

**Tasks**:
- [ ] Escrever README.md
- [ ] Quick start section
- [ ] Requirements section
- [ ] Screenshots
- [ ] Troubleshooting FAQ

**Estimate**: 0.5 dia

---

## 🏗️ Docker Architecture

### Container Structure

```
┌─────────────────────────────────────────────┐
│         Docker Compose Orchestration        │
│                                             │
│  ┌────────────────┐    ┌─────────────────┐ │
│  │   Frontend     │    │    Backend      │ │
│  │   (nginx)      │◄───┤   (FastAPI)     │ │
│  │   Port: 3000   │    │   Port: 8000    │ │
│  └────────────────┘    └─────────────────┘ │
│         │                      │            │
│         └──────────┬───────────┘            │
│                    │                        │
│              ┌─────▼──────┐                │
│              │  Network   │                │
│              │  (bridge)  │                │
│              └────────────┘                │
└─────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
moodlelogsmart/
├── backend/
│   ├── Dockerfile              # Backend container
│   ├── pyproject.toml
│   └── src/
├── frontend/
│   ├── Dockerfile              # Frontend container
│   ├── nginx.conf              # Nginx config
│   ├── package.json
│   └── src/
├── docker-compose.yml          # Orchestration
├── .dockerignore               # Ignore patterns
├── .env.example                # Environment template
└── README.md                   # Quick start
```

---

## 📝 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: moodlelogsmart-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data        # Temporary storage
      - ./rules:/app/rules      # Rule files
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=info
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: moodlelogsmart-frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

networks:
  default:
    driver: bridge
```

---

## 📖 README.md Quick Start

```markdown
# MoodleLogSmart 🧠

Transforme logs do Moodle em análises pedagógicas com 3 cliques.

## Quick Start

```bash
# 1. Clone e inicie
git clone https://github.com/user/moodlelogsmart
cd moodlelogsmart
docker-compose up

# 2. Acesse http://localhost:3000

# 3. Upload CSV → Download ZIP
```

## Pré-requisitos
- Docker 20+
- Docker Compose 2+

## O que você recebe
- ✅ CSV enriquecido com Taxonomia de Bloom
- ✅ XES para process mining (ProM, Disco)
- ✅ Zero configuração necessária

## Troubleshooting
**Porta 3000 ocupada?**
```bash
docker-compose down
# Mude porta no docker-compose.yml: "3001:80"
docker-compose up
```

**Erro de permissão?**
```bash
sudo docker-compose up
```
```

---

## 🧪 Testing Strategy

### Docker Tests
- **Build tests**: 2 test cases
  - Backend image builds successfully
  - Frontend image builds successfully

- **Compose tests**: 3 test cases
  - `docker-compose up` starts both services
  - Health checks pass
  - Services communicate correctly

### Cross-Platform Tests
- **Windows**: Test em Windows 11 + Docker Desktop
- **macOS**: Test em macOS + Docker Desktop
- **Linux**: Test em Ubuntu 22.04 + Docker Engine

### Integration Test
- **E2E**: Upload CSV → Process → Download ZIP (via Docker)

---

## 🚀 Deployment Options (Future)

### MVP: Local Docker
```bash
docker-compose up
```

### Phase 2: Cloud Deployment
- **AWS**: ECS Fargate
- **Azure**: Container Instances
- **GCP**: Cloud Run
- **Railway**: One-click deploy

---

## ✅ Definition of Done

- ✅ Dockerfiles criados (backend + frontend)
- ✅ docker-compose.yml funcional
- ✅ `docker-compose up` funciona em 3 OS
- ✅ README com quick start de 3 linhas
- ✅ Screenshots adicionados
- ✅ Integration test passa

---

## 📊 Success Metrics

- **Setup Time**: <5 minutos para rodar first time
- **Cross-Platform**: Funciona em Windows/macOS/Linux
- **Documentation**: README lido em <2 minutos
- **Troubleshooting**: <10% dos usuários precisam de ajuda

---

**Epic Owner**: @devops (Gage)
**Reviewer**: @architect (Aria)
**Approver**: @pm (Morgan)

---

*Created by Morgan (Product Manager)*
*Last Updated: 2026-01-28*