# Security Best Practices

## Pre-Deployment Security Checklist

- [ ] Strong API keys generated (32+ characters)
- [ ] .env file is not committed to git
- [ ] HTTPS/TLS enabled (for production)
- [ ] CORS properly configured
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Log monitoring set up
- [ ] Backup procedures tested

## API Security

### Generate Secure Keys

```bash
./scripts/generate-secrets.sh
```

### API Key Management

```bash
# In production, rotate keys regularly
# Update .env with new key
API_KEYS=your-new-secure-key

# Restart services
docker-compose restart
```

### Access Control

- API key required for all endpoints
- Header: `X-API-Key: your-api-key`
- Different keys for dev/staging/production

## Network Security

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### HTTPS/TLS

Use reverse proxy (Nginx, Caddy, HAProxy):
- Terminate TLS at proxy
- Force HTTPS redirects
- Use Let's Encrypt certificates

## Container Security

### Base Images

- Always use official images (`python:3.11-slim`, `node:20-alpine`)
- Enable security scanning (`trivy image <image>`)
- Keep images updated

### Non-Root User

Containers run as `appuser` (UID 1000), not root

### Secrets

- No secrets in Dockerfile or image
- Use environment variables only
- .env file never committed to git

## Application Security

### Input Validation

- CSV file validation enabled
- File type checks
- Size limits enforced
- Encoding detection

### SQL Injection Prevention

- N/A (no SQL database in MVP)
- Applicable for future database integration

### CSV Injection Prevention

- Formula character detection
- Data sanitization

## Monitoring & Logging

### Log Monitoring

```bash
# Monitor for errors
docker-compose logs | grep -i error

# Monitor API access
docker-compose logs backend | grep POST
```

### Alert on

- Failed authentication attempts
- File processing errors
- Resource exhaustion
- System errors

## Incident Response

1. **Detect**: Monitor logs and metrics
2. **Contain**: Stop affected containers
3. **Investigate**: Review logs and metrics
4. **Remediate**: Fix issue and restart
5. **Document**: Record incident and fix

## Production Hardening

### Additional Security

- [ ] WAF (Web Application Firewall)
- [ ] DDoS protection
- [ ] API rate limiting
- [ ] Request logging
- [ ] Security audit
- [ ] Penetration testing

### Compliance

- [ ] Data privacy (GDPR, etc.)
- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] Access controls
- [ ] Audit logging

---

See [SECURITY.md](./SECURITY.md) for implementation details
