# Production Deployment Checklist

Complete this checklist before launching to production.

## Pre-Deployment (1 Week Before)

### Planning
- [ ] Define deployment date and time
- [ ] Identify downtime window (if any)
- [ ] Notify stakeholders
- [ ] Prepare rollback plan
- [ ] Schedule post-deployment review

### Environment Setup
- [ ] Prepare production server (2GB RAM, 10GB disk)
- [ ] Install Docker and Docker Compose
- [ ] Configure domain name and DNS
- [ ] Set up SSL/TLS certificate (Let's Encrypt)
- [ ] Configure firewall rules

### Configuration
- [ ] Create .env with production values
- [ ] Generate secure API keys: `./scripts/generate-secrets.sh`
- [ ] Set LOG_LEVEL=WARNING
- [ ] Set DEBUG=false
- [ ] Set VITE_API_URL to production domain
- [ ] Verify .env NOT in .gitignore exclusions

## Pre-Deployment (24 Hours Before)

### Testing
- [ ] Run E2E tests locally: `./scripts/test-e2e.sh`
- [ ] Test upload/process/download flow
- [ ] Verify all API endpoints work
- [ ] Test error scenarios
- [ ] Load test (simulate 10+ concurrent users)

### Security Review
- [ ] Review [SECURITY.md](./SECURITY.md)
- [ ] Verify API keys are strong
- [ ] Check CORS configuration
- [ ] Review network firewall rules
- [ ] Enable security headers
- [ ] Verify TLS certificate valid

### Documentation
- [ ] Update runbooks
- [ ] Document procedures
- [ ] Test disaster recovery
- [ ] Verify backup procedures
- [ ] Review monitoring setup

## Deployment Day

### Before Deployment (1 hour)
- [ ] Notify users of maintenance window (if applicable)
- [ ] Backup current data (if applicable)
- [ ] Have rollback plan ready
- [ ] Have communication channel open

### Deployment (30 minutes)

1. **Clone Code**
   ```bash
   git clone https://github.com/vertumno/moodle-log-smart.git
   cd moodle-log-smart
   ```

2. **Configure**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

3. **Build Images**
   ```bash
   docker-compose build
   ```

4. **Start Services**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

5. **Verify**
   ```bash
   docker-compose ps
   # All services should show "Up" status
   ```

### Post-Deployment Validation (30 minutes)

- [ ] Check container status: `docker-compose ps`
- [ ] Check logs for errors: `docker-compose logs | grep -i error`
- [ ] Test health endpoint: `curl https://api.example.com/api/health`
- [ ] Test frontend: `curl https://example.com`
- [ ] Test upload/download flow manually
- [ ] Verify logs are being written
- [ ] Monitor resource usage: `docker stats`

### Verification Checklist

- [ ] **Backend Running**: `docker inspect moodlelogsmart-backend` shows "running": true
- [ ] **Frontend Running**: `docker inspect moodlelogsmart-frontend` shows "running": true
- [ ] **Backend Healthy**: Health check returns 200
- [ ] **Frontend Accessible**: Returns HTML
- [ ] **API Keys**: Working with X-API-Key header
- [ ] **Uploads**: Can upload test file
- [ ] **Disk Space**: > 5GB free
- [ ] **Memory**: < 80% of limit
- [ ] **Logs**: No CRITICAL or ERROR entries
- [ ] **Monitoring**: Alerts configured and active

## Post-Deployment (2 Hours Later)

- [ ] Monitor logs continuously
- [ ] Monitor resource usage
- [ ] Check for user reports
- [ ] Document any issues found
- [ ] Verify backup jobs ran
- [ ] Conduct post-deployment review

## Post-Deployment (24 Hours Later)

- [ ] Review logs for any issues
- [ ] Performance analysis
- [ ] Document lessons learned
- [ ] Update runbooks based on experience
- [ ] Schedule follow-up review

## Rollback Procedure

If issues occur:

1. **Stop Services**
   ```bash
   docker-compose down
   ```

2. **Restore Previous Code/Data**
   ```bash
   git checkout <previous-commit>
   # Restore backups if needed
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Verify**
   ```bash
   docker-compose ps
   curl http://localhost:8000/api/health
   ```

---

**After Launch**: Continue with [OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md)
