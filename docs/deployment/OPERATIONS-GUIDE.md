# Operations Guide

## Daily Operations

### Health Check

```bash
# Container status
docker-compose ps

# Service health
docker-compose logs | grep -i error

# API health endpoint
curl http://localhost:8000/api/health
```

### Monitor Resources

```bash
# Real-time stats
docker stats

# Disk usage
df -h
du -sh backend/uploads backend/results backend/temp

# Log size
du -sh /var/lib/docker/containers/*/
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last N lines
docker-compose logs --tail=100

# By timestamp
docker-compose logs --since 2h backend
```

## Maintenance Tasks

### Backup

```bash
# Backup volumes
docker run --rm \
  -v moodlelogsmart-backend-uploads:/data \
  -v $(pwd)/backups:/backup \
  ubuntu tar czf /backup/uploads.tar.gz /data

# Backup database (if applicable)
docker-compose exec db pg_dump > backup.sql
```

### Update

```bash
# Pull latest code
git pull

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Verify
docker-compose ps
```

### Clean Old Files

```bash
# Remove files older than 7 days
find backend/results -type f -mtime +7 -delete

# Remove Docker dangling images
docker image prune -f

# Remove dangling volumes
docker volume prune -f
```

### Restart Services

```bash
# Restart backend only
docker-compose restart backend

# Restart all services
docker-compose restart

# Full stop and start
docker-compose down
docker-compose up -d
```

## Monitoring

### Set Up Log Monitoring

```bash
# Watch errors
docker-compose logs -f | grep -i error

# Watch API calls
docker-compose logs -f backend | grep POST
```

### Performance Metrics

Monitor these key metrics:
- **CPU Usage**: Should be < 80% under normal load
- **Memory**: Should be < 80% of allocated
- **Disk**: Keep free space > 20%
- **API Response Time**: Should be < 200ms for health check

### Alerts

Set up alerts for:
- Container down (restart failed)
- High memory usage
- Low disk space
- Error rate spike

## Security

### Regular Maintenance

- **Weekly**: Review logs for errors
- **Monthly**: Update Docker and dependencies
- **Quarterly**: Rotate API keys
- **Annually**: Full security audit

### Secrets Rotation

```bash
# Generate new API key
./scripts/generate-secrets.sh

# Update in .env and restart
docker-compose restart
```

---

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for issues
