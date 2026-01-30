# Environment Variables Reference

## Backend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BACKEND_HOST` | Yes | `0.0.0.0` | Backend server bind address |
| `BACKEND_PORT` | Yes | `8000` | Backend server port |
| `PYTHONUNBUFFERED` | Yes | `1` | Python unbuffered output |
| `API_KEYS` | Yes | - | Comma-separated API keys |
| `MAX_FILE_SIZE_MB` | No | `50` | Maximum upload file size |
| `JOB_TIMEOUT_MINUTES` | No | `10` | Job processing timeout |
| `FILE_RETENTION_HOURS` | No | `24` | Files auto-delete after hours |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `DEBUG` | No | `false` | Enable debug mode |

## Frontend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | Yes | `http://localhost:8000` | Backend API URL |
| `NODE_ENV` | No | `production` | Environment mode |

## Docker & Deployment

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `COMPOSE_PROJECT_NAME` | No | `moodlelogsmart` | Docker Compose project name |

## Example .env Files

### Development
```bash
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_KEYS=dev-key-local-only
VITE_API_URL=http://localhost:8000
LOG_LEVEL=DEBUG
DEBUG=true
```

### Production
```bash
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_KEYS=your-secure-api-key-here
MAX_FILE_SIZE_MB=100
JOB_TIMEOUT_MINUTES=10
FILE_RETENTION_HOURS=24
VITE_API_URL=https://api.example.com
NODE_ENV=production
LOG_LEVEL=WARNING
DEBUG=false
```

---

See `.env.example` for template
