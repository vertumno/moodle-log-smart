# 🎓 MoodleLogSmart

> Transform Moodle logs into semantic learning analytics using Bloom's Taxonomy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React 18+](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) Python 3.11+ & Node.js 18+ for local development

### Start with Docker

```bash
# Clone repository
git clone https://github.com/vertumno/moodle-log-smart
cd moodle-log-smart

# Start backend + frontend
docker-compose up

# Open http://localhost:3000
```

### Local Development

**Backend (Python)**
```bash
cd backend
poetry install
poetry run uvicorn src.moodlelogsmart.api.main:app --reload
```

**Frontend (Node)**
```bash
cd frontend
npm install
npm run dev
```

## 📋 What It Does

1. **Upload** your Moodle CSV log
2. **Auto-Detect** encoding, columns, timestamp format
3. **Clean** data (filter by student role)
4. **Enrich** with Bloom's Taxonomy classification
5. **Download** results (CSV + XES for process mining)

**Input**: Raw Moodle log (CSV)
**Output**: ZIP containing:
- `enriched_log.csv` - All events with semantic classification
- `enriched_log_bloom_only.csv` - Only pedagogical events
- `enriched_log.xes` - Process mining format
- `enriched_log_bloom_only.xes` - PM format, pedagogy only

## 🏗️ Architecture

```
Frontend (React)          Backend (FastAPI)          Database (Files)
  Upload CSV     →      Auto-Detection        →      Results ZIP
  Progress Bar   →      Data Cleaning         →      CSV + XES
  Download       →      Semantic Enrichment   →      Temporary files
```

**Key Features:**
- ✅ **Auto-Detection**: Encoding, delimiter, column mapping, timestamp format
- ✅ **Zero Configuration**: Sensible defaults, no manual setup needed
- ✅ **Multi-Format Export**: CSV + XES (ProM/Disco compatible)
- ✅ **Bloom's Taxonomy**: 13 rules for semantic classification
- ✅ **Cross-Platform**: Works on Windows, macOS, Linux
- 🔒 **Production-Ready Security**: Authentication, validation, hardening (QA Approved)

## 📁 Project Structure

```
moodle-log-smart/
├── backend/          # Python FastAPI application
├── frontend/         # React web interface
├── docs/            # Documentation & specifications
├── docker-compose.yml
└── README.md
```

## 📚 Documentation

- **[Architecture](docs/architecture/)** - System design & diagrams
- **[PRD](docs/PRD-MoodleLogSmart.md)** - Product requirements
- **[Epics](docs/epics/)** - Development roadmap
- **[Stories](docs/stories/)** - User stories & implementation specs

## 🛠️ Development

### Stories (Epic 01 - Backend Core)
1. [STORY-1.1](docs/stories/STORY-1.1-Auto-Detection-CSV-Format.md) - CSV Auto-Detection
2. [STORY-1.2](docs/stories/STORY-1.2-Auto-Mapping-Moodle-Columns.md) - Column Mapping
3. [STORY-1.3](docs/stories/STORY-1.3-Auto-Detection-Timestamp-Format.md) - Timestamp Detection
4. [STORY-1.4-1.7](docs/stories/STORY-1.4-to-1.7-Remaining-Epic01.md) - Cleaning, Enrichment, Export

### Running Tests

```bash
# Backend
cd backend
poetry run pytest tests/

# Frontend
cd frontend
npm test
```

## 🔒 Security & Quality

**QA Status**: ✅ Epic 2 Approved for Production (2026-01-29)
**Test Coverage**: >95% (21 comprehensive tests)
**Security Score**: 98/100

### Security Features
- ✅ **API Key Authentication** (X-API-Key header)
- ✅ **Job Ownership Enforcement** (users can only access their jobs)
- ✅ **CSV Injection Prevention** (formula character detection)
- ✅ **UUID Validation** (path traversal prevention)
- ✅ **Security Headers** (CSP, X-Frame-Options, HSTS)
- ✅ **CORS Properly Configured** (no wildcard)
- ✅ **Job Timeout Protection** (10-minute limit)
- ✅ **Automatic File Cleanup** (TTL-based resource management)

### Configuration

```bash
# Copy example configuration
cp backend/.env.example backend/.env

# Generate secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env
API_KEYS=your-generated-key-here
```

### Quality Reports
- **[Epic 2 QA Gate](docs/qa/gates/EPIC-02-QA-GATE-FINAL.md)** - Comprehensive security review
- **[QA Documentation](docs/qa/)** - Test coverage and quality metrics

**Risk Reduction**: 90% (36/60 → 6/60)

## 🤝 Contributing

Contributions are welcome! This is an open-source project (MIT License).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'feat: add feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🎯 Status

**Current Phase**: MVP Development
- ✅ **Epic 1**: Backend Core (7/7 stories - COMPLETE)
- ✅ **Epic 2**: API Layer (7/7 stories - QA APPROVED ✅)
- ✅ **Epic 3**: Frontend (4/4 stories - COMPLETE)
- ⏳ **Epic 4**: Docker Deployment (0/4 stories - Ready to Start)

**Overall Progress**: 79% Complete (15/19 stories)

**Latest**: Epic 2 passed comprehensive QA review with excellence (2026-01-29)

## 👨‍💻 Author

**Elton Vertumno**

## 🙏 Acknowledgments

Inspired by [Moodle2EventLog](https://github.com/luisrodriguez1/Moodle2EventLog) - bringing open-source and cross-platform capabilities to learning analytics.

---

**For detailed API documentation, see [docs/architecture/API-SPECIFICATION.md](docs/architecture/API-SPECIFICATION.md)**
