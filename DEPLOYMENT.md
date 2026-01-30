# 🚀 Guia de Deployment

Guia completo para fazer deploy do MoodleLogSmart em produção usando **Vercel** (Frontend) e **Render** (Backend).

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Deployment Frontend (Vercel)](#deployment-frontend-vercel)
4. [Deployment Backend (Render)](#deployment-backend-render)
5. [Configuração de Variáveis](#configuração-de-variáveis)
6. [Verificação de Produção](#verificação-de-produção)
7. [Troubleshooting](#troubleshooting)

---

## 👀 Visão Geral

```
GitHub Repository
     │
     ├─→ main branch ─→ Vercel (Frontend Staging)
     │                → Render (Backend Staging)
     │
     └─→ v*.*.* tag ─→ Vercel (Frontend Production)
                      → Render (Backend Production)
```

### Arquitetura de Deployment

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUÇÃO                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend (Vercel)              Backend (Render)        │
│  https://moodle-log-smart       https://moodle-log-     │
│  .vercel.app                    smart-backend.onrender. │
│       │                         com                     │
│       │                              │                  │
│       └──────────────┬───────────────┘                  │
│                      │                                   │
│              API Calls (HTTPS)                           │
│              X-API-Key Auth                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Pré-requisitos

### Contas Necessárias

- [ ] **GitHub**: Repositório clonado e acesso push
- [ ] **Vercel**: Conta ativa (free tier OK)
- [ ] **Render**: Conta ativa (free/paid tier)
- [ ] **Git**: Instalado localmente

### Configuração Local

```bash
# Verificar Git
git --version

# Login no GitHub via CLI
gh auth login

# Verificar remotes
git remote -v
# origin → seu fork ou upstream
# upstream → repositório original (se forked)
```

---

## 🔧 Deployment Frontend (Vercel)

### 1. Conectar Repositório ao Vercel

**Passo 1: Acesse Vercel**
- Vá para https://vercel.com
- Faça login com GitHub
- Clique em "Add New Project"

**Passo 2: Importe Repositório**
- Selecione `moodle-log-smart`
- Vercel detectará Next.js/Vite automaticamente
- Configure:
  ```
  Framework: Vite
  Root Directory: ./frontend
  Build Command: npm run build
  Output Directory: dist
  Install Command: npm install
  ```

### 2. Configure Variáveis de Ambiente

No painel Vercel → Settings → Environment Variables:

```bash
# Staging (Branch Preview / main)
VITE_API_URL=https://moodle-log-smart-backend.onrender.com

# Production (Production)
VITE_API_URL=https://moodle-log-smart-backend.onrender.com
```

### 3. Configure Branches

**Staging Deployment** (Vercel → Settings → Git):
```
Production Branch: main
Preview Branches: feature/*
```

### 4. Deploy Automático

```bash
# Local: Faça push
git push origin main

# Vercel: Detectará automáticamente e iniciará build
# Acompanhe em: https://vercel.com/moodle-log-smart
```

### 5. Verificar Deployment

```bash
# Testar staging
https://moodle-log-smart.vercel.app

# Testar production (após tag)
git tag v1.0.0
git push origin v1.0.0
# Vercel criará deployments para preview + production
```

---

## 🔧 Deployment Backend (Render)

### 1. Conectar Repositório ao Render

**Passo 1: Acesse Render**
- Vá para https://render.com
- Faça login com GitHub
- Clique em "New +" → "Web Service"

**Passo 2: Conecte Repositório**
- Selecione `moodle-log-smart`
- Configure:
  ```
  Name: moodle-log-smart-backend
  Environment: Python 3
  Build Command: pip install poetry && poetry install --no-dev
  Start Command: poetry run uvicorn src.moodlelogsmart.main:app --host 0.0.0.0 --port $PORT
  ```

**Passo 3: Configure Build Settings**
- Runtime: Python 3.11
- Root Directory: `backend`
- Region: US East (ou mais próximo)

### 2. Configure Variáveis de Ambiente

No painel Render → Environment Variables:

```bash
# Python
PYTHON_VERSION=3.11

# API Configuration
API_KEYS=SEU_CHAVE_API_AQUI
MAX_FILE_SIZE_MB=50

# FastAPI
DEBUG=false
LOG_LEVEL=info

# Temporary Files
UPLOAD_DIR=/tmp/uploads
JOBS_DIR=/tmp/jobs
CLEANUP_INTERVAL_HOURS=1
JOB_TIMEOUT_MINUTES=10

# Bloom Taxonomy
BLOOM_RULES_ENABLED=true

# CORS
CORS_ORIGINS=https://moodle-log-smart.vercel.app

# Database (opcional, para futuro)
# DATABASE_URL=postgresql://...
```

**Gerar chave API segura:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Deploy Automático

```bash
# Render monitora Branch automáticamente
# Push para main → Deploy automático em staging
git push origin main

# Tag para production
git tag v1.0.0
git push origin v1.0.0
# Render pode ser configurado para deployer tags para production
```

### 4. Verificar Deployment

```bash
# Testar health check
curl https://moodle-log-smart-backend.onrender.com/health

# Resposta esperada:
# {"status":"healthy","timestamp":"2024-01-15T10:30:45.123456"}

# Testar API docs
https://moodle-log-smart-backend.onrender.com/docs
```

---

## 🔐 Configuração de Variáveis

### Backend (.env)

```bash
# Backend/src/moodlelogsmart/.env

# ============ API CONFIGURATION ============
API_KEYS=chave-secreta-longa-aqui
MAX_FILE_SIZE_MB=50
ALLOWED_MIME_TYPES=text/csv,application/vnd.ms-excel

# ============ FASTAPI ============
DEBUG=false
LOG_LEVEL=info
CORS_ORIGINS=https://moodle-log-smart.vercel.app,http://localhost:3000

# ============ FILE SYSTEM ============
UPLOAD_DIR=/tmp/uploads
JOBS_DIR=/tmp/jobs
CLEANUP_INTERVAL_HOURS=1
JOB_TIMEOUT_MINUTES=10

# ============ FEATURE FLAGS ============
BLOOM_RULES_ENABLED=true
ENABLE_RATE_LIMITING=true

# ============ DATABASE (Futuro) ============
# DATABASE_URL=postgresql://user:password@host/db
```

### Frontend (.env)

```bash
# Frontend/.env

# ============ API CONFIGURATION ============
VITE_API_URL=https://moodle-log-smart-backend.onrender.com
VITE_API_TIMEOUT_MS=60000

# ============ FEATURE FLAGS ============
VITE_ENABLE_TELEMETRY=false
VITE_ENVIRONMENT=production
```

### Sincronizar Secrets

```bash
# Em Render / Vercel, use a UI para adicionar secrets
# Não comita .env em git!

# Arquivo .gitignore já contém:
.env
.env.local
.env.*.local
```

---

## ✅ Verificação de Produção

### Checklist de Deploy

- [ ] **Frontend**
  - [ ] Build completa sem erros
  - [ ] CSS/JS carrega corretamente
  - [ ] Imagens exibem
  - [ ] Links funcionam

- [ ] **Backend**
  - [ ] Health check retorna 200
  - [ ] API docs acessível em `/docs`
  - [ ] Endpoints respondendo
  - [ ] CORS configurado corretamente

- [ ] **Integração Frontend-Backend**
  - [ ] Upload de arquivo funciona
  - [ ] Status é consultado corretamente
  - [ ] Download retorna arquivo ZIP
  - [ ] Erros são tratados

- [ ] **Segurança**
  - [ ] API Key obrigatória (401 sem ela)
  - [ ] HTTPS enforçado
  - [ ] CORS sem wildcard
  - [ ] Security headers presentes

### Testes de Funcionalidade

```bash
# 1. Testar Upload
curl -X POST https://moodle-log-smart-backend.onrender.com/api/upload \
  -H "X-API-Key: sua-chave-api" \
  -F "file=@exemplo.csv"
# Esperar: {"job_id": "...", "status": "processing"}

# 2. Testar Status
curl https://moodle-log-smart-backend.onrender.com/api/status/{job_id} \
  -H "X-API-Key: sua-chave-api"
# Esperar: {"status": "processing", "progress": 50, ...}

# 3. Testar Download
curl https://moodle-log-smart-backend.onrender.com/api/download/{job_id} \
  -H "X-API-Key: sua-chave-api" \
  -o resultado.zip
# Esperar: arquivo ZIP baixado

# 4. Testar UI
# Abrir https://moodle-log-smart.vercel.app
# Fazer upload de arquivo
# Acompanhar progresso
# Baixar resultado
```

---

## 🐛 Troubleshooting

### Frontend Build Falha

**Erro**: `Build failed: command failed with exit code 1`

**Solução**:
```bash
# Limpar e reconstruir localmente
cd frontend
npm ci  # clean install
npm run build
# Se passou localmente, problema pode ser no Vercel
# Verifique: Node version, variáveis de ambiente
```

### Backend Deploy Falha

**Erro**: `Build failed: poetry install timeout`

**Solução**:
```bash
# Verificar pyproject.toml
cd backend
poetry lock --no-update
git add poetry.lock
git commit -m "update poetry.lock"
git push origin main
# Retry deploy
```

### CORS Error

**Erro**: `Access-Control-Allow-Origin` missing

**Verificar**:
```bash
# No backend, CORS_ORIGINS deve incluir Frontend URL
curl -i -X OPTIONS https://moodle-log-smart-backend.onrender.com/api/upload

# Esperar headers:
# Access-Control-Allow-Origin: https://moodle-log-smart.vercel.app
# Access-Control-Allow-Methods: GET, POST, OPTIONS
```

**Solução**:
```bash
# Backend/.env
CORS_ORIGINS=https://moodle-log-smart.vercel.app
# Redeploy
```

### API Key Não Aceita

**Erro**: `401 Unauthorized: Invalid or missing API key`

**Verificar**:
```bash
# Testar com cURL
curl -H "X-API-Key: CHAVE_AQUI" \
  https://moodle-log-smart-backend.onrender.com/health

# Se falhar, chave está errada ou não configurada
# Verificar em Render → Environment Variables
```

### Timeout em Upload

**Erro**: `504 Gateway Timeout`

**Causas**:
- Arquivo muito grande (>50MB)
- Processamento lento
- Job timeout de 10 minutos

**Solução**:
```bash
# Verificar tamanho do arquivo
# Se < 50MB: aguarde, pode ser só processamento lento
# Se >= 50MB: divida em arquivos menores

# Aumentar timeout (se necessário):
# Backend/.env
# JOB_TIMEOUT_MINUTES=15
# Redeploy
```

### Espaço em Disco

**Erro**: `Disk space exhausted` em Render

**Causa**: Arquivos temporários não sendo limpos

**Solução**:
```bash
# Render deleta /tmp automaticamente a cada deploy
# Garantir limpeza periódica no código:
# Backend/.env
CLEANUP_INTERVAL_HOURS=1

# Ou fazer limpeza manual via SSH:
# Render → Service → Shell
# rm -rf /tmp/uploads/* /tmp/jobs/*
```

---

## 📊 Monitoramento

### Logs em Produção

**Vercel**:
- Dashboard → Deployments → Logs
- Filtrar por: build, runtime, edge

**Render**:
- Dashboard → Service → Logs
- Live tail: `tail -f logs`

### Métricas

**Vercel**:
- Analytics → Web Vitals (CLS, LCP, FID)
- Functions → Execution time, memory

**Render**:
- Metrics → CPU, Memory, Disk
- Network → Requests/sec, Response time

---

## 🔄 Ciclo de Release

### Preparar Release

```bash
# 1. Atualize versão
# package.json (frontend) & pyproject.toml (backend)
# Versão: MAJOR.MINOR.PATCH (seguindo Semantic Versioning)

# 2. Atualize CHANGELOG.md
# Documente features, fixes, breaking changes

# 3. Teste localmente
cd backend && poetry run pytest
cd ../frontend && npm test

# 4. Commit
git commit -m "chore: bump version to v1.0.0"
```

### Fazer Release

```bash
# 1. Create tag
git tag v1.0.0
git push origin v1.0.0

# 2. GitHub: Create Release
# Vá para Releases → Create Release
# Adicione changelog
# Mark como "Latest Release"

# 3. Verificar deployments
# Vercel → Deployments (deve ver novo deploy com tag)
# Render → Deploy History (deve ver novo deploy com tag)

# 4. Testar em Produção
# Vercel: https://moodle-log-smart.vercel.app
# Render: curl https://moodle-log-smart-backend.onrender.com/health
```

---

## 🆘 Suporte

- 📖 [Documentação Vercel](https://vercel.com/docs)
- 📖 [Documentação Render](https://render.com/docs)
- 🐛 [Issues](https://github.com/vertumno/moodle-log-smart/issues)
- 💬 [Discussions](https://github.com/vertumno/moodle-log-smart/discussions)

---

**Última Atualização**: 2026-01-30

**Próximo Passo**: Veja [ARCHITECTURE.md](./docs/ARCHITECTURE.md) para entender design do sistema
