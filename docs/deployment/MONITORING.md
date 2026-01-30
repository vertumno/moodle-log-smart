# Monitoring & Logging Guide

## Container Logs

### View Logs

```bash
# All services
docker-compose logs

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last N lines
docker-compose logs --tail=100

# Time range
docker-compose logs --since 1h
```

### Log Format

```
timestamp [service] level message
```

Example:
```
2026-01-29T17:30:45.123456 backend INFO API request: POST /api/upload
```

## Container Metrics

### Resource Usage

```bash
# Real-time stats
docker stats

# Single snapshot
docker stats --no-stream

# Check memory limits
docker inspect moodlelogsmart-backend | grep -A 10 '"Memory'
```

### Key Metrics

- **CPU**: Usage percentage and cores
- **Memory**: Usage vs. limit
- **Network**: I/O bytes
- **Processes**: Running processes

## Health Checks

### Manual Health Check

```bash
# Backend
curl http://localhost:8000/api/health
# Response: {"status":"healthy","version":"1.0.0"}

# Frontend
curl http://localhost:3000
# Response: HTML page
```

### Docker Health Status

```bash
# Check status
docker inspect --format='{{.State.Health.Status}}' moodlelogsmart-backend

# Expected: healthy, starting, or unhealthy
```

## Performance Monitoring

### Disk Usage

```bash
# Total usage
df -h

# By directory
du -sh backend/*

# Old files
find backend/results -type f -mtime +30
```

### Log Size

```bash
# Docker logs size
du -sh /var/lib/docker/containers/*/

# Rotate logs
docker-compose logs --tail=0 > /dev/null
```

## Advanced Monitoring

### Prometheus + Grafana (Optional)

```yaml
# In docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana:latest
  ports:
    - "3001:3000"
  depends_on:
    - prometheus
```

### ELK Stack (Optional)

```yaml
# Elasticsearch + Logstash + Kibana
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
```

## Alerting

### Set Up Alerts for

- Container down
- High memory (> 80%)
- High CPU (> 80%)
- Low disk space (< 20%)
- Error rate spike
- API latency spike

### Example Alert (using CloudWatch, DataDog, etc.)

```bash
# Monitor memory
watch -n 10 'docker stats --no-stream | grep moodlelogsmart'

# Alert if CPU > 80% or Memory > 80%
```

---

See [OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md) for daily tasks
