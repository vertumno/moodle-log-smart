# Troubleshooting Guide

## Container Issues

### Backend Won't Start

**Symptoms**: Container exits with error

**Diagnosis**:
```bash
docker-compose logs backend
docker inspect moodlelogsmart-backend
```

**Common Causes & Solutions**:

1. **Missing .env file**
   ```bash
   cp .env.example .env
   docker-compose restart backend
   ```

2. **Port 8000 already in use**
   ```bash
   # Find process on port 8000
   lsof -i :8000

   # Or change port in .env
   BACKEND_PORT=8001
   ```

3. **Insufficient disk space**
   ```bash
   df -h
   # Clean up: docker system prune
   ```

### Frontend Won't Start

**Symptoms**: Frontend container exits or doesn't respond

**Solution**:
```bash
docker-compose logs frontend
# Check port 3000 not in use
lsof -i :3000
```

### Cannot Connect to Backend

**Symptoms**: Frontend shows network errors

**Diagnosis**:
```bash
# Check network
docker network ls
docker network inspect moodlelogsmart-network

# Test connectivity
docker exec moodlelogsmart-frontend \
  curl http://backend:8000/api/health
```

**Solution**:
```bash
# Update VITE_API_URL in .env
VITE_API_URL=http://backend:8000  # For development
VITE_API_URL=https://api.example.com  # For production
```

## API Issues

### 401 Unauthorized

**Cause**: Missing or invalid API key

**Solution**:
```bash
# Check API key in header
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/health

# Generate new key
./scripts/generate-secrets.sh
```

### 413 Payload Too Large

**Cause**: File exceeds MAX_FILE_SIZE_MB

**Solution**:
```bash
# In .env, increase limit
MAX_FILE_SIZE_MB=200
```

### 500 Internal Server Error

**Solution**:
```bash
docker-compose logs backend | tail -50
# Check for specific error messages
```

## Performance Issues

### Slow Processing

**Cause**: Insufficient resources or large file

**Solution**:
```bash
# Check resource usage
docker stats

# For production, increase limits in docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### High Memory Usage

**Solution**:
```bash
# Restart containers
docker-compose restart

# Check for memory leaks
docker stats --no-stream

# Reduce file size limits
MAX_FILE_SIZE_MB=50
```

## File/Volume Issues

### Files Not Persisting

**Cause**: Volume not mounted correctly

**Solution**:
```bash
# Check volumes
docker volume ls
docker volume inspect moodlelogsmart-backend-uploads

# Verify docker-compose.yml has:
volumes:
  - ./backend/uploads:/app/uploads
```

### Disk Space Full

**Solution**:
```bash
# Clean old files
find ./backend/results -type f -mtime +7 -delete

# Or enable auto-cleanup (Story 2.6)
FILE_RETENTION_HOURS=24
```

## Network Issues

### Cannot Access from External Host

**Solution**:
```bash
# Check firewall
sudo ufw allow 80,443

# For development, use IP instead of localhost
curl http://YOUR_IP:3000
```

### DNS Not Resolving

**For custom domain**:
```bash
# Verify DNS
nslookup api.example.com

# Update .env
VITE_API_URL=https://api.example.com
```

## Log Issues

### Logs Too Large

**Solution**: Already configured with rotation
```yaml
logging:
  options:
    max-size: "10m"
    max-file: "3"
```

### Cannot Find Logs

**Location**: Docker logs stored at
```bash
/var/lib/docker/containers/*/
```

**View**:
```bash
docker-compose logs -f
docker-compose logs --tail=100 backend
```

## Health Check Issues

### Healthcheck Failing

**Solution**:
```bash
# Manually test endpoint
curl http://localhost:8000/api/health

# Increase timeout if slow
# In docker-compose.yml:
healthcheck:
  timeout: 20s  # Increase from 10s
```

## Getting Help

1. **Check logs**: `docker-compose logs`
2. **Check status**: `docker-compose ps`
3. **Review docs**: See [OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md)
4. **Report issue**: GitHub issues with logs and error details

---

**See Also**: [OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md), [DOCKER-BUILD-GUIDE.md](./DOCKER-BUILD-GUIDE.md)
