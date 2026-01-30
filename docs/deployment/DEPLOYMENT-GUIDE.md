# Deployment Guide - MoodleLogSmart

**Version**: 1.0
**Last Updated**: 2026-01-29

## Prerequisites

- **Docker** v20.10+ and **Docker Compose** v1.29+
- **2GB RAM** minimum (4GB recommended)
- **10GB disk space** minimum
- **Git** for cloning repository
- **Python 3.8+** (for helper scripts)

## Local Development

### Setup

```bash
# 1. Clone repository
git clone https://github.com/vertumno/moodle-log-smart.git
cd moodle-log-smart

# 2. Create environment file
cp .env.example .env

# 3. (Optional) Generate API key
./scripts/generate-secrets.sh

# 4. Start services
docker-compose up -d

# 5. Verify
docker-compose ps
curl http://localhost:8000/api/health
```

### Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Single Server Deployment

### Linux VPS Setup

```bash
# 1. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# 3. Clone and configure
git clone https://github.com/vertumno/moodle-log-smart.git
cd moodle-log-smart

# 4. Create .env with production values
cp .env.example .env
nano .env  # Edit with production API key

# 5. Start production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 6. Verify
docker-compose ps
docker-compose logs
```

### Domain & HTTPS Setup

With Caddy reverse proxy:

```bash
# Create Caddyfile
cat > Caddyfile << 'EOF'
api.example.com {
  reverse_proxy localhost:8000
}

example.com {
  reverse_proxy localhost:3000
}
EOF

# Run Caddy
docker pull caddy
docker run -d \
  -p 80:80 -p 443:443 \
  -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data \
  --network moodlelogsmart-network \
  caddy
```

Update `.env`:
```bash
VITE_API_URL=https://api.example.com
```

## Cloud Deployment

### AWS EC2

```bash
# 1. Launch t3.medium instance (2GB RAM, 2vCPU)
# 2. Connect via SSH
# 3. Follow "Single Server Deployment" steps
# 4. Configure security group:
#    - Allow 80 (HTTP) from 0.0.0.0/0
#    - Allow 443 (HTTPS) from 0.0.0.0/0
#    - Allow 22 (SSH) from your IP
```

### Google Cloud Run

```bash
# Note: Cloud Run requires stateless containers
# MoodleLogSmart has file storage, so use Cloud Storage

# Deploy with Terraform or gcloud CLI
gcloud run deploy moodle-log-smart \
  --image gcr.io/your-project/moodlelogsmart:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml moodlelogsmart

# Scale services
docker service scale moodlelogsmart_backend=3
```

## Post-Deployment

### Health Check

```bash
# Container health
docker-compose ps

# API health
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","version":"1.0.0"}

# Frontend
curl http://localhost:3000
# Expected: HTML response
```

### Logs Verification

```bash
# Check for errors
docker-compose logs | grep -i error

# Backend startup
docker-compose logs backend | head -20

# Frontend startup
docker-compose logs frontend | head -20
```

### Test Upload/Download

```bash
# Create test file
echo "Time,Event name,Component,User full name
1/15/24, 10:30,Course module viewed,File,Test User" > test.csv

# Upload
JOB_ID=$(curl -s -X POST \
  -F "file=@test.csv" \
  -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/upload | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Check status
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/status/$JOB_ID

# Download (when complete)
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/download/$JOB_ID \
  -o results.zip
```

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues.

---

**Next**: Review [SECURITY.md](./SECURITY.md) for production hardening.
