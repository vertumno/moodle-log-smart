# Docker Build Guide - MoodleLogSmart

**Last Updated**: 2026-01-29
**Version**: 1.0

## Quick Start

### Build Backend
```bash
cd backend
docker build -t moodlelogsmart-backend:latest .
```

### Build Frontend
```bash
cd frontend
docker build -t moodlelogsmart-frontend:latest .
```

### Build Both
```bash
docker-compose build
```

---

## Performance Targets

| Image | Target Size | Build Time | Current |
|-------|-------------|-----------|---------|
| Backend | < 500MB | < 3 min | ⏳ TBD |
| Frontend | < 200MB | < 2 min | ⏳ TBD |

---

## Architecture Overview

### Backend Dockerfile Optimization

**Strategy**: Multi-stage build with dependency caching

**Stages**:
1. **Builder** (python:3.11-slim)
   - Install Poetry
   - Copy pyproject.toml, poetry.lock
   - Install dependencies with `poetry install --no-dev`
   - Creates virtual environment in `.venv`

2. **Runtime** (python:3.11-slim)
   - Copy virtual environment from builder
   - Copy source code
   - Create non-root user (appuser:1000)
   - Expose port 8000
   - Healthcheck on `/api/health`

**Why this is optimal**:
- ✅ Final image excludes Poetry and build tools (smaller)
- ✅ Virtual environment copied (faster startup)
- ✅ `.venv` cached separately from source code
- ✅ Dependencies only rebuilt if pyproject.toml changes
- ✅ Uses python:3.11-slim (no dev packages)

### Frontend Dockerfile Optimization

**Strategy**: Multi-stage build with production serving

**Stages**:
1. **Builder** (node:20-alpine)
   - Copy package.json, package-lock.json
   - Install dependencies with `npm ci` (faster, reproducible)
   - Copy source code
   - Build: `npm run build`
   - Creates `/dist` folder

2. **Runtime** (node:20-alpine)
   - Install `serve` package (lightweight HTTP server)
   - Copy only `/dist` folder from builder
   - Create non-root user (appuser:1000)
   - Expose port 3000
   - Healthcheck on port 3000

**Why this is optimal**:
- ✅ Final image excludes build tools (much smaller)
- ✅ Alpine image (minimal base)
- ✅ Only `serve` installed in runtime (no full npm)
- ✅ `node_modules` not in final image
- ✅ npm ci vs npm install (reproducible installs)

---

## .dockerignore Strategy

### Backend .dockerignore

Excludes files that aren't needed at runtime:

```
__pycache__          # Python bytecode (regenerated)
*.pyc, *.pyo, *.pyd  # Compiled Python files
.pytest_cache        # Test artifacts
.coverage            # Code coverage reports
htmlcov/             # Coverage HTML
dist/, build/        # Build artifacts
*.egg-info/          # Package metadata
.env                 # Local env (use at runtime)
.venv                # Local venv (not needed in container)
*.log                # Log files
.git                 # Git history (not needed)
README.md, docs/     # Documentation
tests/               # Test files
.mypy_cache          # Type checking cache
.ruff_cache          # Linting cache
```

**Result**: Smaller build context, faster builds

### Frontend .dockerignore

```
node_modules         # NPM packages (reinstalled)
dist                 # Build output (recreated)
build                # Old build directory
.git                 # Git history
*.md                 # Documentation
.env*                # Environment files
.vscode, .idea       # IDE configs
coverage/, .cache    # Build artifacts
```

**Important**: Does NOT exclude:
- ✅ `package.json` (dependencies)
- ✅ `package-lock.json` (dependency lock)
- ✅ `src/` (source code)
- ✅ `public/` (static assets)
- ✅ `index.html` (HTML template)

---

## Build Caching Strategy

### How Docker Layer Caching Works

Docker caches layers based on:
1. Base image
2. Dockerfile instructions (RUN, COPY, etc.)
3. File modifications

**Optimal layer ordering** (least → most frequently changed):

```dockerfile
# Layer 1: Base image (rarely changes)
FROM python:3.11-slim

# Layer 2: Install tools (rarely changes)
RUN apt-get update && apt-get install -y curl

# Layer 3: Copy dependency files (changes when deps updated)
COPY pyproject.toml poetry.lock ./

# Layer 4: Install dependencies (rebuilds if Layer 3 changes)
RUN poetry install --no-dev

# Layer 5: Copy source code (changes frequently)
COPY src ./src

# Layer 6: Setup (rebuilds if Layer 5 changes)
RUN useradd appuser && chown -R appuser /app
```

### Cache Efficiency

**Good**:
```bash
# First build: ~3 minutes
docker build -t app:latest .

# Second build (no changes): Uses all cached layers
docker build -t app:latest .
# Result: ~5 seconds (cached)

# Third build (only source changed):
# Rebuilds layers 5-6, reuses 1-4
# Result: ~30 seconds
```

**Cache Busting**:
```bash
# Force rebuild without cache
docker build --no-cache -t app:latest .
```

---

## Testing Builds

### Validate Syntax

```bash
# Backend
cd backend
docker build -t moodlelogsmart-backend:test .

# Frontend
cd frontend
docker build -t moodlelogsmart-frontend:test .
```

### Check Image Sizes

```bash
docker images | grep moodlelogsmart

# Expected output:
# moodlelogsmart-backend    latest    abc123    300MB
# moodlelogsmart-frontend   latest    def456    150MB
```

### Verify Non-Root User

```bash
docker run --rm moodlelogsmart-backend:test whoami
# Expected: appuser

docker run --rm moodlelogsmart-frontend:test whoami
# Expected: appuser
```

### Test Healthcheck

```bash
# Start backend
docker run -d --name test-backend moodlelogsmart-backend:test

# Wait for healthcheck
sleep 35

# Check status
docker inspect test-backend | grep -A 5 '"Health"'
# Expected: "Status": "healthy"

# Cleanup
docker rm -f test-backend
```

### Validate Incremental Builds

```bash
# Time first build
time docker build -t test:latest ./backend

# Time second build (cached)
time docker build -t test:latest ./backend

# Expected:
# First: ~180 seconds (3 minutes)
# Second: ~5 seconds (cached)
```

---

## Security Scanning with Trivy

### Install Trivy

**macOS**:
```bash
brew install trivy
```

**Linux**:
```bash
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | tee /etc/apt/sources.list.d/trivy.list
apt-get update && apt-get install trivy
```

**Windows** (via Docker):
```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image moodlelogsmart-backend:test
```

### Run Security Scan

```bash
# Scan backend
trivy image moodlelogsmart-backend:test

# Scan frontend
trivy image moodlelogsmart-frontend:test

# Save report to file
trivy image --format json moodlelogsmart-backend:test > backend-scan.json
trivy image --format sarif moodlelogsmart-frontend:test > frontend-scan.sarif
```

### Interpret Results

**Output Example**:
```
moodlelogsmart-backend:test

Total: 2 (CRITICAL: 0, HIGH: 0, MEDIUM: 2, LOW: 5)

Medium
   CVE-2024-1234 (python-package)
   Affected: package >= 2.0.0
   Fixed: 2.1.0
```

**Action**:
- ✅ CRITICAL: Fix immediately
- ✅ HIGH: Fix before production
- ⚠️ MEDIUM: Plan update
- ℹ️ LOW: Monitor

---

## Multi-Architecture Builds

### Single Architecture (Default)

```bash
# Builds for current system only
docker build -t moodlelogsmart-backend:latest ./backend
```

### Multi-Architecture (Advanced)

Requires Docker buildx:

```bash
# Check buildx availability
docker buildx ls

# Create builder
docker buildx create --name mybuilder
docker buildx use mybuilder

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 \
  -t moodlelogsmart-backend:latest ./backend

# Push to registry
docker buildx build --platform linux/amd64,linux/arm64 \
  -t registry.example.com/backend:latest \
  --push ./backend
```

---

## Troubleshooting

### Build Fails: "pip install poetry failed"

**Cause**: Network issues or Python version mismatch

**Solution**:
```bash
# Check Python version
docker run --rm python:3.11-slim python --version

# Try with explicit mirrors (if in restricted environment)
docker build --build-arg PIP_INDEX_URL=https://pypi.org/simple \
  -t app:test ./backend
```

### Build Too Slow

**Cause**: Docker daemon thrashing, or network issues

**Solution**:
```bash
# Increase Docker resources in Docker Desktop settings:
# - CPU: 4+ cores
# - Memory: 4GB+
# - Disk: 50GB+ for images

# Or use BuildKit (faster):
DOCKER_BUILDKIT=1 docker build -t app:test .
```

### Image Too Large

**Cause**: Cached node_modules or Python packages in final image

**Solution**:
- ✅ Use multi-stage build (copy only final artifacts)
- ✅ Use `.dockerignore` properly
- ✅ Use alpine base images (smaller)
- ✅ Remove build tools from runtime stage

### Healthcheck Fails

**Cause**: Port not exposed or health endpoint failing

**Solution**:
```bash
# Test healthcheck manually
docker run -d --name test app:latest
sleep 10
curl http://localhost:8000/api/health

# Or enter container
docker exec -it test bash
curl http://localhost:8000/api/health
```

---

## Optimization Checklist

- ✅ Multi-stage build (separate build and runtime)
- ✅ Layer order (least → most frequently changed)
- ✅ Use slim/alpine base images
- ✅ .dockerignore excludes unnecessary files
- ✅ Non-root user (security)
- ✅ Healthcheck configured
- ✅ EXPOSE port documented
- ✅ Build args for flexibility
- ✅ Security scanning enabled
- ✅ Build time < targets (3 min backend, 2 min frontend)

---

## Production Deployment

### Build for Production

```bash
# With tags
docker build -t moodlelogsmart-backend:1.0.0 ./backend
docker build -t moodlelogsmart-frontend:1.0.0 ./frontend

# With registry
docker build -t registry.example.com/backend:1.0.0 ./backend
docker push registry.example.com/backend:1.0.0
```

### Use docker-compose

```bash
# Build all images
docker-compose build

# Start services
docker-compose up -d

# Verify
docker-compose ps
```

---

## References

- [Docker Build Best Practices](https://docs.docker.com/build/building/best-practices/)
- [Docker Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Trivy Scanner](https://aquasecurity.github.io/trivy/)
- [Docker Buildx](https://docs.docker.com/build/architecture/)

---

**Document Owner**: @dev (Dex)
**Last Updated**: 2026-01-29
**Related Stories**: STORY-4.1, STORY-4.2, STORY-4.3
