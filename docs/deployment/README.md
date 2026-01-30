# MoodleLogSmart Deployment Documentation

Welcome to the deployment guides for MoodleLogSmart. This directory contains everything you need to deploy, operate, and maintain the system.

## 📋 Quick Index

| Document | Purpose | Audience |
|----------|---------|----------|
| **[DOCKER-BUILD-GUIDE.md](./DOCKER-BUILD-GUIDE.md)** | Build optimization & security scanning | Developers, DevOps |
| **[DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)** | How to deploy locally, on-premises, cloud | System Admins |
| **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** | Common issues & solutions | Everyone |
| **[OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md)** | Daily operations & maintenance | System Admins |
| **[ENVIRONMENT-VARIABLES.md](./ENVIRONMENT-VARIABLES.md)** | Configuration reference | Developers |
| **[SECURITY.md](./SECURITY.md)** | Security best practices & hardening | DevOps, Security |
| **[MONITORING.md](./MONITORING.md)** | Logging, metrics, monitoring | DevOps |
| **[PRODUCTION-CHECKLIST.md](./PRODUCTION-CHECKLIST.md)** | Pre-launch validation | DevOps |

---

## 🚀 Quick Start (3 Steps)

### 1. Prepare Environment
```bash
# Copy environment template
cp .env.example .env

# Generate secure API key
./scripts/generate-secrets.sh
```

### 2. Start Services
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Verify Deployment
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test endpoint
curl http://localhost:8000/api/health
curl http://localhost:3000
```

---

## 📚 Documentation Structure

### For Local Development
1. Start with: [DOCKER-BUILD-GUIDE.md](./DOCKER-BUILD-GUIDE.md)
2. Then read: [ENVIRONMENT-VARIABLES.md](./ENVIRONMENT-VARIABLES.md)
3. Reference: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### For Production Deployment
1. Review: [PRODUCTION-CHECKLIST.md](./PRODUCTION-CHECKLIST.md)
2. Follow: [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)
3. Harden: [SECURITY.md](./SECURITY.md)
4. Maintain: [OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md)

### For Operations
1. Daily tasks: [OPERATIONS-GUIDE.md](./OPERATIONS-GUIDE.md)
2. Issues: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
3. Monitoring: [MONITORING.md](./MONITORING.md)

---

## 🔑 Key Concepts

### Environment Variables
All configuration is via `.env` file. See [ENVIRONMENT-VARIABLES.md](./ENVIRONMENT-VARIABLES.md) for complete reference.

### Docker Compose Profiles
- **Development** (default): Hot reload, verbose logging, development API key
- **Production**: No hot reload, optimized resources, secure defaults

```bash
# Development
docker-compose up -d

# Production (with overrides)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Secrets Management
- Generate API keys: `./scripts/generate-secrets.sh`
- Store in `.env` (never commit to git)
- Rotate regularly in production

---

## ✅ Deployment Checklist

Before going live, complete:

- [ ] Review [PRODUCTION-CHECKLIST.md](./PRODUCTION-CHECKLIST.md)
- [ ] Run E2E tests: `./scripts/test-e2e.sh`
- [ ] Review [SECURITY.md](./SECURITY.md)
- [ ] Configure monitoring
- [ ] Plan backup procedures
- [ ] Document runbooks

---

## 🆘 Getting Help

### Common Issues
See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for solutions to:
- Container won't start
- API not responding
- Performance problems
- Disk space issues
- Log file management

### Support Resources
- **GitHub Issues**: Report bugs and feature requests
- **Docker Docs**: https://docs.docker.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/

---

## 📞 Version & Support

- **MoodleLogSmart**: v1.0.0 (MVP)
- **Last Updated**: 2026-01-30
- **Deployment Docs**: v1.0
- **Status**: ✅ Production Ready

For detailed technical specifications, see the main README.md in project root.

---

**Next**: Start with [DOCKER-BUILD-GUIDE.md](./DOCKER-BUILD-GUIDE.md) or [DEPLOYMENT-GUIDE.md](./DEPLOYMENT-GUIDE.md)
