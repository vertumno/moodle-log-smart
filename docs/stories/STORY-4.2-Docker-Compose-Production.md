# Story 4.2: Docker Compose Production Configuration

**Story ID**: STORY-4.2
**Epic**: EPIC-04 (Docker + Deployment)
**Status**: Ready for Development
**Priority**: P0 (Must-Have)
**Sprint**: Sprint 4
**Assigned to**: @dev (Dex)
**Estimate**: 0.5 dia

---

## 📖 User Story

**As a** system administrator
**I want** production-ready Docker Compose configuration
**So that** deployment is secure, reliable, and properly configured

---

## ✅ Acceptance Criteria

- [ ] Environment variables via .env file template
- [ ] Resource limits configured (CPU, memory)
- [ ] Restart policies set (on-failure)
- [ ] Logging configured with rotation
- [ ] Secrets managed securely (no hardcoded values)
- [ ] Development vs Production profiles supported
- [ ] Volume persistence validated
- [ ] Networks properly isolated
- [ ] docker-compose.prod.yml created

---

## 🎯 Context & Requirements

### Current State
- ✅ Basic docker-compose.yml exists
- ✅ Backend and frontend services defined
- ✅ Networks configured
- ✅ Volumes configured
- ✅ Healthchecks implemented

### What Needs Enhancement
- ⚠️ No .env file template
- ⚠️ No resource limits
- ⚠️ Default restart policy (not production-ready)
- ⚠️ No logging configuration
- ⚠️ No separate dev/prod profiles
- ⚠️ API keys hardcoded or not configured

### Dependencies
- **Story 4.1**: Optimized Docker images
- **Epic 2**: API authentication implemented (Story 2.5)

---

## 📋 Implementation Tasks

### Task 1: Create .env Template
**Subtasks:**
- [ ] Create `.env.example` in project root
- [ ] Document all required environment variables
- [ ] Add comments explaining each variable
- [ ] Create `.env.development` for local dev
- [ ] Add .env to .gitignore (if not already)

**Variables to include:**
```bash
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
PYTHONUNBUFFERED=1

# API Security
API_KEYS=your-generated-api-key-here

# File Management
MAX_FILE_SIZE_MB=50
TEMP_DIR=/app/temp
UPLOADS_DIR=/app/uploads
RESULTS_DIR=/app/results

# Job Configuration
JOB_TIMEOUT_MINUTES=10
FILE_RETENTION_HOURS=24

# Frontend Configuration
VITE_API_URL=http://localhost:8000

# Docker Configuration
COMPOSE_PROJECT_NAME=moodlelogsmart

# Logging
LOG_LEVEL=INFO
```

### Task 2: Add Resource Limits
**Subtasks:**
- [ ] Define CPU limits for backend
- [ ] Define memory limits for backend
- [ ] Define CPU limits for frontend
- [ ] Define memory limits for frontend
- [ ] Test limits don't cause OOM errors
- [ ] Document resource requirements

**Resource Configuration:**
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  frontend:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Task 3: Configure Restart Policies
**Subtasks:**
- [ ] Set restart policy for backend
- [ ] Set restart policy for frontend
- [ ] Test restart on failure
- [ ] Document restart behavior

**Restart Configuration:**
```yaml
services:
  backend:
    restart: unless-stopped

  frontend:
    restart: unless-stopped
```

### Task 4: Logging Configuration
**Subtasks:**
- [ ] Configure log driver (json-file)
- [ ] Set max log file size
- [ ] Set log rotation (max files)
- [ ] Test log rotation works
- [ ] Document log access commands

**Logging Configuration:**
```yaml
services:
  backend:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=backend"

  frontend:
    logging:
      driver: json-file
      options:
        max-size: "5m"
        max-file: "3"
        labels: "service=frontend"
```

### Task 5: Create Production Compose File
**Subtasks:**
- [ ] Create `docker-compose.prod.yml`
- [ ] Override development settings
- [ ] Remove development-specific volumes (hot reload)
- [ ] Configure for production environment
- [ ] Document usage

**Production Overrides:**
- Remove source code volume mounts
- Add health check intervals
- Configure production API URLs
- Set production log levels

### Task 6: Secret Management
**Subtasks:**
- [ ] Document API key generation
- [ ] Remove any hardcoded secrets
- [ ] Use environment variables for all secrets
- [ ] Add secret generation script
- [ ] Document secret rotation procedure

**Secret Generation Script:**
```bash
#!/bin/bash
# generate-secrets.sh

echo "Generating API key..."
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

echo ""
echo "Add this to your .env file:"
echo "API_KEYS=$API_KEY"
echo ""
echo "Keep this key secure!"
```

### Task 7: Development Profile
**Subtasks:**
- [ ] Keep current docker-compose.yml for development
- [ ] Add hot-reload volumes for development
- [ ] Configure development ports
- [ ] Document dev vs prod differences

**Development Features:**
- Source code mounted as volumes (hot reload)
- Exposed ports for debugging
- Verbose logging
- No resource limits (for development flexibility)

---

## 🧪 Testing Strategy

### Configuration Tests

1. **Test: .env File Loads Correctly**
   ```bash
   cp .env.example .env
   # Edit .env with test values
   docker-compose config
   # Expected: No errors, variables interpolated
   ```

2. **Test: Resource Limits Enforced**
   ```bash
   docker-compose up -d
   docker stats
   # Expected: Memory usage < configured limits
   ```

3. **Test: Restart Policy Works**
   ```bash
   docker-compose up -d
   docker kill moodlelogsmart-backend
   sleep 10
   docker ps | grep moodlelogsmart-backend
   # Expected: Container restarted automatically
   ```

4. **Test: Logging Configuration**
   ```bash
   docker-compose logs --tail=100 backend
   ls -lh /var/lib/docker/containers/*/
   # Expected: Log files exist, rotation working
   ```

5. **Test: Production Compose File**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml config
   # Expected: Production overrides applied
   ```

6. **Test: Secrets Not Exposed**
   ```bash
   docker-compose config | grep -i "api_key"
   # Expected: No plaintext secrets visible
   ```

7. **Test: Volume Persistence**
   ```bash
   # Upload file, stop containers, restart
   docker-compose down
   docker-compose up -d
   # Expected: Files still present in volumes
   ```

---

## 📝 Implementation Checklist

### Planning
- [x] Current docker-compose.yml reviewed
- [x] Production requirements identified
- [x] Security considerations documented

### Development
- [ ] .env.example created
- [ ] Resource limits added
- [ ] Restart policies configured
- [ ] Logging configured
- [ ] docker-compose.prod.yml created
- [ ] Secret generation script created

### Testing
- [ ] All configuration tests passing
- [ ] Resource limits validated
- [ ] Restart policy verified
- [ ] Logging rotation works
- [ ] Production profile tested

### Documentation
- [ ] .env variables documented
- [ ] Dev vs Prod differences documented
- [ ] Secret management guide created

---

## 📊 Production Configuration Comparison

| Feature | Development | Production |
|---------|-------------|------------|
| Source volumes | ✅ Mounted | ❌ Not mounted |
| Resource limits | ❌ None | ✅ CPU/Memory limits |
| Restart policy | ❌ no | ✅ unless-stopped |
| Log rotation | ❌ Default | ✅ 10MB/3 files |
| API Keys | ⚠️ Test keys | ✅ Generated secrets |
| Ports exposed | ✅ All | ✅ Only necessary |
| Debug logging | ✅ Verbose | ❌ INFO level |

---

## 📁 File List

**Files to Create:**
- [ ] `.env.example` - Environment variable template
- [ ] `.env.development` - Development defaults
- [ ] `docker-compose.prod.yml` - Production overrides
- [ ] `scripts/generate-secrets.sh` - Secret generation utility
- [ ] `docs/deployment/ENVIRONMENT-VARIABLES.md` - Env var documentation

**Files to Modify:**
- [ ] `docker-compose.yml` - Add resource limits, logging, restart
- [ ] `.gitignore` - Ensure .env is ignored
- [ ] `README.md` - Update deployment instructions

**Files to Validate:**
- [ ] `docker-compose.yml` - Configuration syntax
- [ ] `.env.example` - All required variables present

---

## 🔗 Dependencies & Blockers

**Depends on:**
- ✅ Story 4.1: Optimized Docker images
- ✅ Story 2.5: API authentication implemented

**Blocks:**
- Story 4.3: Integration Testing (needs production config)
- Story 4.4: Deployment Documentation (needs final config)

**External Dependencies:**
- Docker Compose v2+ installed
- Environment variable support in deployment environment

---

## 🛠️ Technical Details

### Docker Compose File Structure

```yaml
# docker-compose.yml (development + base)
version: '3.8'

services:
  backend:
    build: ./backend
    restart: unless-stopped
    env_file: .env
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./backend/src:/app/src  # Hot reload
      - backend-uploads:/app/uploads
      - backend-results:/app/results
      - backend-temp:/app/temp
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    networks:
      - moodlelogsmart-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

  frontend:
    build: ./frontend
    restart: unless-stopped
    env_file: .env
    depends_on:
      - backend
    ports:
      - "3000:3000"
    networks:
      - moodlelogsmart-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    logging:
      driver: json-file
      options:
        max-size: "5m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s

networks:
  moodlelogsmart-network:
    driver: bridge

volumes:
  backend-uploads:
  backend-results:
  backend-temp:
```

```yaml
# docker-compose.prod.yml (production overrides)
version: '3.8'

services:
  backend:
    volumes:
      # Remove source code volume (no hot reload in production)
      - backend-uploads:/app/uploads
      - backend-results:/app/results
      - backend-temp:/app/temp
    environment:
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1

  frontend:
    environment:
      - NODE_ENV=production
```

### Usage

**Development:**
```bash
docker-compose up
```

**Production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 📚 References

**Docker Compose Documentation:**
- https://docs.docker.com/compose/compose-file/
- https://docs.docker.com/compose/environment-variables/
- https://docs.docker.com/config/containers/logging/

**Best Practices:**
- https://docs.docker.com/compose/production/
- https://docs.docker.com/config/containers/resource_constraints/

**Related Stories:**
- Story 2.5: Authentication & Authorization (API keys)
- Story 4.1: Dockerfiles Optimization
- Story 4.3: Integration Testing E2E

---

## ✨ Notes for Developer

**Priority Order:**
1. Create .env.example (critical for deployment)
2. Add resource limits (prevent resource exhaustion)
3. Configure restart policies (reliability)
4. Setup logging (observability)
5. Create production profile (deployment readiness)

**Security Reminders:**
- ✅ Never commit .env files to git
- ✅ Generate unique API keys per environment
- ✅ Use strong secrets (32+ characters)
- ✅ Document secret rotation procedures

**Testing Checklist:**
- Test with minimal resources (512MB RAM)
- Test restart after crash
- Test log rotation after 10MB
- Test with production profile

---

**Created**: 2026-01-29
**Status**: ✅ Ready for Development
**Assigned**: @dev (Dex)
